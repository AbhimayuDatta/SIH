#!/usr/bin/env python3
"""
Build a REAL-data training set from the CWC daily water-level workbook
(Water_Level_Readings_in_Brahmaputra_Valley.xlsx).

Unlike generate_data.py (fully synthetic), this uses actual official danger
levels and HFL (highest flood level) per station to derive a genuine
elevation-margin-based risk label -- directly implementing the project's
"risk should be relative to the local danger line, not an absolute number"
principle, because station zero-datums differ by ~28m to ~105m and are not
comparable in absolute terms.

Limitations (be aware of these before training on this alone):
  - Only water_level, rate_of_rise (day-over-day), and elevation_margin are
    real. There's no rainfall / soil moisture / upstream-agreement /
    evacuation-time in this workbook, so those fields are simply omitted
    per-record (format_sensor_reading already handles missing fields
    gracefully).
  - Readings are DAILY, not hourly, so rate_of_rise here is a coarse
    24h-averaged figure, not the true instantaneous rate your sensor mesh
    would report.
  - Only 6 stations, ~1.5 seasons of data (May 2018-Oct 2019) -> a few
    hundred rows. Treat this as a real-anchored supplement to the synthetic
    set, not a replacement for it.
"""

import json
import re
from datetime import datetime
from pathlib import Path
import argparse

import openpyxl

STATIONS = ['DIBRUGARH', 'NEMATIGHAT', 'TEZPUR', 'GUWAHATI D.C COURT', 'GOALPARA', 'DHUBRI']
COL_OFFSETS = [2, 7, 12, 17, 22, 27]  # DANGER LEVEL column for each station block

# Reused directly from generate_data.py's THRESHOLDS so real and synthetic
# labels mean the same thing.
ELEVATION_MARGIN_THRESHOLDS = {'panic': 0.3, 'high': 0.8, 'low': 1.5, 'normal': 3.0}
RATE_OF_RISE_THRESHOLDS = {'normal': 0.05, 'low': 0.15, 'high': 0.30, 'panic': 0.50}


def _parse_date(value):
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _parse_level(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s.upper() in ('NA', 'N/A', '-'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _score_descending(value, t):
    if value <= t['panic']:
        return 3
    elif value <= t['high']:
        return 2
    elif value <= t['low']:
        return 1
    return 0


def _score_ascending(value, t):
    if value >= t['panic']:
        return 3
    elif value >= t['high']:
        return 2
    elif value >= t['low']:
        return 1
    return 0


def _label_from_score(weighted_score):
    if weighted_score >= 2.5:
        return 'PANIC'
    elif weighted_score >= 1.5:
        return 'HIGH-ALERT'
    elif weighted_score >= 0.5:
        return 'LOW-ALERT'
    return 'NORMAL'


def build_dataset(xlsx_path: str) -> list:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb['Sheet2']
    rows = list(ws.iter_rows(values_only=True))

    danger_row = rows[3]
    station_meta = {}
    for name, off in zip(STATIONS, COL_OFFSETS):
        station_meta[name] = {
            'danger_level': danger_row[off],
            'hfl': danger_row[off + 1],
        }

    # per-station time series for rate-of-rise computation
    series = {name: [] for name in STATIONS}

    for row in rows[3:]:
        date = _parse_date(row[0])
        if date is None:
            continue
        for name, off in zip(STATIONS, COL_OFFSETS):
            level = _parse_level(row[off + 2])
            if level is not None:
                series[name].append((date, level))

    records = []
    for name in STATIONS:
        readings = sorted(series[name], key=lambda x: x[0])
        danger_level = station_meta[name]['danger_level']
        prev_date, prev_level = None, None

        for date, level in readings:
            elevation_margin = round(danger_level - level, 3)

            rate_of_rise = None
            if prev_date is not None:
                hours = (date - prev_date).total_seconds() / 3600.0
                if hours > 0:
                    rate_of_rise = round((level - prev_level) / hours, 4)

            elev_score = _score_descending(elevation_margin, ELEVATION_MARGIN_THRESHOLDS)
            if rate_of_rise is not None and rate_of_rise > 0:
                rate_score = _score_ascending(rate_of_rise, RATE_OF_RISE_THRESHOLDS)
                # weights match generate_data.py's ratio (elevation 0.10 : rate 0.20 -> 1:2), renormalized
                weighted_score = elev_score * (1 / 3) + rate_score * (2 / 3)
            else:
                weighted_score = elev_score

            label = _label_from_score(weighted_score)

            record = {
                'station': name,
                'river_level': level,
                'danger_level': danger_level,
                'elevation_margin': elevation_margin,
                'label': label,
                'timestamp': date.isoformat(),
                'source': 'real:cwc_daily_readings',
            }
            if rate_of_rise is not None:
                record['rate_of_rise'] = rate_of_rise

            records.append(record)
            prev_date, prev_level = date, level

    return records


def main():
    parser = argparse.ArgumentParser(description='Build real-data training set from CWC xlsx')
    parser.add_argument('--xlsx', type=str, required=True, help='Path to the water level xlsx')
    parser.add_argument('--output', type=str, default='./data/real_cwc.json', help='Output JSON path')
    args = parser.parse_args()

    records = build_dataset(args.xlsx)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(records, f, indent=2)

    dist = {}
    for r in records:
        dist[r['label']] = dist.get(r['label'], 0) + 1

    print(f"Built {len(records)} real records from {args.xlsx}")
    print("\nLabel distribution:")
    for label in ['NORMAL', 'LOW-ALERT', 'HIGH-ALERT', 'PANIC']:
        count = dist.get(label, 0)
        print(f"  {label:12s}: {count:4d} ({count/len(records)*100:.1f}%)" if records else "  (no data)")

    print("\nPer-station record counts:")
    station_counts = {}
    for r in records:
        station_counts[r['station']] = station_counts.get(r['station'], 0) + 1
    for s, c in station_counts.items():
        print(f"  {s:20s}: {c}")

    print(f"\nSaved to {args.output}")


if __name__ == '__main__':
    main()

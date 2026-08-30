#!/usr/bin/env python3
"""
Generate synthetic flood sensor data for training.
Replace with real sensor/CWC/IMD data when available.

Feature set follows the multi-factor risk model from ASSAM_FLOOD_ALERT_SYSTEM.md:

    Risk = f(
        current water level,
        rate of rise,
        predicted water level,
        upstream rainfall,
        cumulative rainfall,
        soil saturation,
        river travel time / upstream sensor agreement,
        local elevation margin,
        evacuation time available
    )

Labels map onto the 4-stage plan (Green/Yellow/Orange/Red ->
NORMAL/LOW-ALERT/HIGH-ALERT/PANIC), with the explicit rule from the
project notes: a warning should NOT be based on riverbank height alone.
It must also account for elevation margin and evacuation time.
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import argparse


# Risk thresholds (adjust based on your location/sensors and CWC danger levels)
THRESHOLDS = {
    'water_level':        {'normal': 1.0, 'low': 2.0, 'high': 3.0, 'panic': 4.0},        # m
    'rate_of_rise':       {'normal': 0.05, 'low': 0.15, 'high': 0.30, 'panic': 0.50},     # m/hr
    'predicted_water_level_2hr': {'normal': 1.5, 'low': 2.5, 'high': 3.5, 'panic': 4.5},  # m, +2hr forecast
    'upstream_rainfall_6hr': {'normal': 10, 'low': 30, 'high': 60, 'panic': 100},         # mm, 6hr rolling
    'antecedent_precip_index': {'normal': 15, 'low': 40, 'high': 70, 'panic': 100},       # API (decay-weighted mm)
    'soil_moisture':      {'normal': 40, 'low': 60, 'high': 80, 'panic': 95},             # %
    'river_level':        {'normal': 2.0, 'low': 3.5, 'high': 5.0, 'panic': 6.5},         # m
    'forecast_rainfall_6hr': {'normal': 10, 'low': 30, 'high': 60, 'panic': 100},         # mm
    # Lower elevation_margin = house/shelter closer to the danger line = worse.
    # This is what stops a "riverbank-only" threshold from missing a low-lying village.
    'elevation_margin':   {'panic': 0.3, 'high': 0.8, 'low': 1.5, 'normal': 3.0},         # m, descending risk
    # Less evacuation_time_min = worse. Also descending risk.
    'evacuation_time_min': {'panic': 20, 'high': 45, 'low': 90, 'normal': 180},           # minutes
}


def assess_risk(sample: dict) -> str:
    """Determine risk level from sensor readings using the project's weighted multi-factor model."""

    def score_ascending(value, key):
        t = THRESHOLDS[key]
        if value >= t['panic']:
            return 3
        elif value >= t['high']:
            return 2
        elif value >= t['low']:
            return 1
        return 0

    def score_descending(value, key):
        # Lower value = higher risk (elevation margin, evacuation time)
        t = THRESHOLDS[key]
        if value <= t['panic']:
            return 3
        elif value <= t['high']:
            return 2
        elif value <= t['low']:
            return 1
        return 0

    water_level_score   = score_ascending(sample.get('water_level', 0), 'water_level')
    rate_of_rise_score  = score_ascending(sample.get('rate_of_rise', 0), 'rate_of_rise')
    predicted_score     = score_ascending(sample.get('predicted_water_level_2hr', 0), 'predicted_water_level_2hr')
    upstream_rain_score = score_ascending(sample.get('upstream_rainfall_6hr', 0), 'upstream_rainfall_6hr')
    api_score            = score_ascending(sample.get('antecedent_precip_index', 0), 'antecedent_precip_index')
    soil_score           = score_ascending(sample.get('soil_moisture', 0), 'soil_moisture')
    river_score          = score_ascending(sample.get('river_level', 0), 'river_level')
    forecast_rain_score  = score_ascending(sample.get('forecast_rainfall', 0), 'forecast_rainfall_6hr')
    elevation_score      = score_descending(sample.get('elevation_margin', 3.0), 'elevation_margin')
    evac_time_score      = score_descending(sample.get('evacuation_time_min', 180), 'evacuation_time_min')

    scores = [
        water_level_score, rate_of_rise_score, predicted_score, upstream_rain_score,
        api_score, soil_score, river_score, forecast_rain_score, elevation_score, evac_time_score,
    ]

    # Weights: rate of rise and predicted level get more weight than raw current level
    # (per project notes: ARRV / forecast-crossing matters more than a static reading).
    # Elevation margin and evacuation time are weighted highly because they encode the
    # "not just riverbank height" refinement -- the same water level is far more dangerous
    # for a low, slow-to-evacuate village than a high, well-connected one.
    weights = [
        0.15,  # water_level
        0.20,  # rate_of_rise
        0.15,  # predicted_water_level_2hr
        0.10,  # upstream_rainfall_6hr
        0.05,  # antecedent_precip_index
        0.05,  # soil_moisture
        0.05,  # river_level
        0.05,  # forecast_rainfall
        0.10,  # elevation_margin
        0.10,  # evacuation_time_min
    ]

    weighted_score = sum(s * w for s, w in zip(scores, weights))

    # Two-or-more-upstream-sensor agreement is a hard gate, per the project's
    # "Maybe better" rule: don't alert Orange/Red off a single isolated sensor.
    if not sample.get('upstream_sensor_agreement', True):
        weighted_score = min(weighted_score, 1.4)  # cap at high end of LOW-ALERT

    if weighted_score >= 2.5:
        return 'PANIC'
    elif weighted_score >= 1.5:
        return 'HIGH-ALERT'
    elif weighted_score >= 0.5:
        return 'LOW-ALERT'
    else:
        return 'NORMAL'


# ---------------------------------------------------------------------------
# Banded sampling: each severity generator must produce values that actually
# land in the scoring band assess_risk() expects. Sampling uniformly across a
# range that straddles two threshold bands (the original bug) silently
# mislabels a large fraction of "HIGH-ALERT"/"PANIC" samples as lower tiers,
# because most of a wide uniform range falls short of the 'high'/'panic' cut.
# These helpers sample strictly within the band for a target score (0-3),
# with a jitter margin, so generated severity matches the assessed label.
# ---------------------------------------------------------------------------

# Purely descriptive fields (not weighted in assess_risk) still get realistic
# generation ranges so the text the LLM sees looks coherent.
_DISPLAY_THRESHOLDS = {
    'rainfall':   {'normal': 5, 'low': 15, 'high': 30, 'panic': 50},
    'flow_rate':  {'normal': 50, 'low': 150, 'high': 300, 'panic': 500},
}


def _ascending_band(thresholds: dict, key: str, score: int) -> float:
    t = thresholds[key]
    bounds = [0.0, t['low'], t['high'], t['panic'], t['panic'] * 1.6]
    lo, hi = bounds[score], bounds[score + 1]
    return random.uniform(lo, hi)


def _descending_band(thresholds: dict, key: str, score: int) -> float:
    t = thresholds[key]
    # bounds ordered low-value(worst) -> high-value(best)
    bounds = [0.0, t['panic'], t['high'], t['low'], t['low'] * 1.8]
    idx = 3 - score
    lo, hi = bounds[idx], bounds[idx + 1]
    return random.uniform(lo, hi)


def _generate_for_score(target_score: int, agreement_p: float) -> dict:
    """Build a sample whose fields sit in the band matching target_score (0=Green ... 3=Red)."""
    a = lambda key: round(_ascending_band(THRESHOLDS, key, target_score), 3)
    d = lambda key: round(_descending_band(THRESHOLDS, key, target_score), 3)
    disp = lambda key: round(_ascending_band(_DISPLAY_THRESHOLDS, key, target_score), 1)

    return {
        'water_level': a('water_level'),
        'rate_of_rise': a('rate_of_rise'),
        'predicted_water_level_2hr': a('predicted_water_level_2hr'),
        'rainfall': disp('rainfall'),
        'upstream_rainfall_6hr': a('upstream_rainfall_6hr'),
        'antecedent_precip_index': a('antecedent_precip_index'),
        'flow_rate': disp('flow_rate'),
        'soil_moisture': a('soil_moisture'),
        'river_level': a('river_level'),
        'forecast_rainfall': a('forecast_rainfall_6hr'),
        'elevation_margin': d('elevation_margin'),
        'evacuation_time_min': round(_descending_band(THRESHOLDS, 'evacuation_time_min', target_score)),
        'upstream_sensor_agreement': random.random() < agreement_p,
    }


def generate_normal() -> dict:
    return _generate_for_score(0, agreement_p=0.95)


def generate_low_alert() -> dict:
    return _generate_for_score(1, agreement_p=0.9)


def generate_high_alert() -> dict:
    return _generate_for_score(2, agreement_p=0.85)


def generate_panic() -> dict:
    return _generate_for_score(3, agreement_p=0.85)


def generate_sample() -> dict:
    """Generate a single sample with timestamp."""
    # Bias toward normal conditions (realistic distribution)
    rand = random.random()
    if rand < 0.55:
        sample = generate_normal()
    elif rand < 0.80:
        sample = generate_low_alert()
    elif rand < 0.95:
        sample = generate_high_alert()
    else:
        sample = generate_panic()

    # Add noise to numeric fields
    for k, v in sample.items():
        if k == 'upstream_sensor_agreement':
            continue
        sample[k] = round(v * random.uniform(0.95, 1.05), 3)

    # soil_moisture is a percentage; the open-ended PANIC jitter band can push it past 100
    sample['soil_moisture'] = min(sample['soil_moisture'], 100.0)

    # Assess true label using the full multi-factor model
    label = assess_risk(sample)
    sample['label'] = label

    # Add timestamp
    base_time = datetime.now() - timedelta(days=30)
    sample['timestamp'] = (base_time + timedelta(
        hours=random.randint(0, 720),
        minutes=random.randint(0, 59)
    )).isoformat()

    return sample


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic flood sensor data')
    parser.add_argument('--train-samples', type=int, default=2000, help='Training samples')
    parser.add_argument('--val-samples', type=int, default=500, help='Validation samples')
    parser.add_argument('--output-dir', type=str, default='./data', help='Output directory')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.train_samples} training samples...")
    train_data = [generate_sample() for _ in range(args.train_samples)]

    print(f"Generating {args.val_samples} validation samples...")
    val_data = [generate_sample() for _ in range(args.val_samples)]

    train_path = Path(args.output_dir) / 'train.json'
    val_path = Path(args.output_dir) / 'val.json'

    with open(train_path, 'w') as f:
        json.dump(train_data, f, indent=2)

    with open(val_path, 'w') as f:
        json.dump(val_data, f, indent=2)

    for name, data in [('Train', train_data), ('Val', val_data)]:
        dist = {}
        for s in data:
            dist[s['label']] = dist.get(s['label'], 0) + 1
        print(f"\n{name} distribution:")
        for label in ['NORMAL', 'LOW-ALERT', 'HIGH-ALERT', 'PANIC']:
            count = dist.get(label, 0)
            print(f"  {label:12s}: {count:4d} ({count/len(data)*100:.1f}%)")

    print(f"\nSaved to {train_path} and {val_path}")


if __name__ == '__main__':
    main()

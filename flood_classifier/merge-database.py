#!/usr/bin/env python3
"""
Merge synthetic (generate_data.py) and real (build_real_dataset.py) data into
final train/val JSON files for train_qlora.py.

Real records are split by STATION, not randomly by row, so that all of a
given station's flood season ends up in either train or val -- otherwise a
model could "memorize" a station's specific danger-level arithmetic from
train and just replay it on a held-out day from the same event, which
inflates val accuracy without meaning much.
"""

import json
import random
import argparse
from pathlib import Path
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description='Merge synthetic and real datasets')
    parser.add_argument('--synthetic-train', default='./data/train.json')
    parser.add_argument('--synthetic-val', default='./data/val.json')
    parser.add_argument('--real', default='./data/real_cwc.json')
    parser.add_argument('--real-val-stations', nargs='+',
                         default=['GOALPARA', 'DHUBRI'],
                         help='Stations held out entirely for validation (default: 2 of 6)')
    parser.add_argument('--output-train', default='./data/train_merged.json')
    parser.add_argument('--output-val', default='./data/val_merged.json')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    with open(args.synthetic_train) as f:
        synth_train = json.load(f)
    with open(args.synthetic_val) as f:
        synth_val = json.load(f)
    with open(args.real) as f:
        real = json.load(f)

    by_station = defaultdict(list)
    for r in real:
        by_station[r['station']].append(r)

    real_train, real_val = [], []
    for station, records in by_station.items():
        if station in args.real_val_stations:
            real_val.extend(records)
        else:
            real_train.extend(records)

    train = synth_train + real_train
    val = synth_val + real_val
    random.shuffle(train)
    random.shuffle(val)

    Path(args.output_train).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_train, 'w') as f:
        json.dump(train, f, indent=2)
    with open(args.output_val, 'w') as f:
        json.dump(val, f, indent=2)

    def dist(data):
        d = {}
        for r in data:
            d[r['label']] = d.get(r['label'], 0) + 1
        return d

    print(f"Train: {len(train)} total ({len(synth_train)} synthetic + {len(real_train)} real)")
    print(f"  {dist(train)}")
    print(f"Val:   {len(val)} total ({len(synth_val)} synthetic + {len(real_val)} real)")
    print(f"  {dist(val)}")
    print(f"\nReal-only validation stations (held out entirely from train): {args.real_val_stations}")
    print(f"Saved to {args.output_train} and {args.output_val}")


if __name__ == '__main__':
    main()

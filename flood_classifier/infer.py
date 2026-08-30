#!/usr/bin/env python3
"""
Flood Risk Classifier Inference for Raspberry Pi 5
Supports ONNX (recommended for Pi 5) and PyTorch backends
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

LABEL2ID = {"NORMAL": 0, "LOW-ALERT": 1, "HIGH-ALERT": 2, "PANIC": 3}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}


class FloodClassifierONNX:
    """ONNX Runtime inference (fastest on Pi 5)."""
    
    def __init__(self, onnx_path: str, tokenizer_path: str, max_length: int = 256):
        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError("Install onnxruntime: pip install onnxruntime")
        
        # Use CPU provider (Pi 5 has no GPU)
        providers = ['CPUExecutionProvider']
        self.session = ort.InferenceSession(onnx_path, providers=providers)
        
        # Load tokenizer
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.max_length = max_length
        
        # Warm up
        dummy = self.tokenizer(
            "Water Level: 1.0m; Rainfall (1hr): 5.0mm",
            return_tensors='np',
            max_length=max_length,
            padding='max_length',
            truncation=True,
        )
        self.session.run(None, {
            'input_ids': dummy['input_ids'].astype(np.int64),
            'attention_mask': dummy['attention_mask'].astype(np.int64),
        })
        print(f"ONNX model loaded: {onnx_path}")
    
    def predict(self, sensor_data: Dict) -> Tuple[str, float, Dict[str, float]]:
        """Predict risk level from sensor readings."""
        text = self._format_input(sensor_data)
        
        inputs = self.tokenizer(
            text,
            return_tensors='np',
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
        )
        
        ort_inputs = {
            'input_ids': inputs['input_ids'].astype(np.int64),
            'attention_mask': inputs['attention_mask'].astype(np.int64),
        }
        
        start = time.perf_counter()
        logits = self.session.run(None, ort_inputs)[0]
        latency_ms = (time.perf_counter() - start) * 1000
        
        probs = self._softmax(logits[0])
        pred_id = int(np.argmax(probs))
        confidence = float(probs[pred_id])
        
        all_probs = {ID2LABEL[i]: float(probs[i]) for i in range(4)}
        
        return ID2LABEL[pred_id], confidence, all_probs
    
    def _format_input(self, data: Dict) -> str:
        parts = []
        if 'water_level' in data:
            parts.append(f"Water Level: {data['water_level']:.2f}m")
        if 'rate_of_rise' in data:
            parts.append(f"Rate of Rise: {data['rate_of_rise']:.3f}m/hr")
        if 'predicted_water_level_2hr' in data:
            parts.append(f"Predicted Water Level (+2hr): {data['predicted_water_level_2hr']:.2f}m")
        if 'rainfall' in data:
            parts.append(f"Rainfall (1hr): {data['rainfall']:.1f}mm")
        if 'upstream_rainfall_6hr' in data:
            parts.append(f"Upstream Rainfall (6hr): {data['upstream_rainfall_6hr']:.1f}mm")
        if 'antecedent_precip_index' in data:
            parts.append(f"Antecedent Precipitation Index: {data['antecedent_precip_index']:.1f}")
        if 'flow_rate' in data:
            parts.append(f"Flow Rate: {data['flow_rate']:.1f}m³/s")
        if 'soil_moisture' in data:
            parts.append(f"Soil Moisture: {data['soil_moisture']:.1f}%")
        if 'river_level' in data:
            parts.append(f"River Level: {data['river_level']:.2f}m")
        if 'forecast_rainfall' in data:
            parts.append(f"Forecast Rainfall (6hr): {data['forecast_rainfall']:.1f}mm")
        if 'upstream_sensor_agreement' in data:
            agree = "Yes" if data['upstream_sensor_agreement'] else "No (isolated reading, treat as suspicious)"
            parts.append(f"Upstream Sensor Agreement: {agree}")
        if 'elevation_margin' in data:
            parts.append(f"Elevation Margin Above Danger Line: {data['elevation_margin']:.2f}m")
        if 'evacuation_time_min' in data:
            parts.append(f"Estimated Evacuation Time Available: {data['evacuation_time_min']:.0f}min")
        return f"Flood Sensor Readings: {'; '.join(parts)}"
    
    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()


class FloodClassifierPyTorch:
    """PyTorch inference (fallback if ONNX not available)."""
    
    def __init__(self, model_path: str, max_length: int = 256):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        from peft import PeftModel
        
        self.device = torch.device('cpu')
        self.max_length = max_length
        
        # Load base model + LoRA adapters
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            device_map='cpu',
        )
        self.model = model.to(self.device)
        self.model.eval()
        print(f"PyTorch model loaded: {model_path}")
    
    def predict(self, sensor_data: Dict) -> Tuple[str, float, Dict[str, float]]:
        text = self._format_input(sensor_data)
        
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        import torch
        start = time.perf_counter()
        with torch.no_grad():
            logits = self.model(**inputs).logits
        latency_ms = (time.perf_counter() - start) * 1000
        
        probs = torch.softmax(logits[0], dim=-1).cpu().numpy()
        pred_id = int(np.argmax(probs))
        confidence = float(probs[pred_id])
        
        all_probs = {ID2LABEL[i]: float(probs[i]) for i in range(4)}
        
        return ID2LABEL[pred_id], confidence, all_probs
    
    def _format_input(self, data: Dict) -> str:
        parts = []
        if 'water_level' in data:
            parts.append(f"Water Level: {data['water_level']:.2f}m")
        if 'rate_of_rise' in data:
            parts.append(f"Rate of Rise: {data['rate_of_rise']:.3f}m/hr")
        if 'predicted_water_level_2hr' in data:
            parts.append(f"Predicted Water Level (+2hr): {data['predicted_water_level_2hr']:.2f}m")
        if 'rainfall' in data:
            parts.append(f"Rainfall (1hr): {data['rainfall']:.1f}mm")
        if 'upstream_rainfall_6hr' in data:
            parts.append(f"Upstream Rainfall (6hr): {data['upstream_rainfall_6hr']:.1f}mm")
        if 'antecedent_precip_index' in data:
            parts.append(f"Antecedent Precipitation Index: {data['antecedent_precip_index']:.1f}")
        if 'flow_rate' in data:
            parts.append(f"Flow Rate: {data['flow_rate']:.1f}m³/s")
        if 'soil_moisture' in data:
            parts.append(f"Soil Moisture: {data['soil_moisture']:.1f}%")
        if 'river_level' in data:
            parts.append(f"River Level: {data['river_level']:.2f}m")
        if 'forecast_rainfall' in data:
            parts.append(f"Forecast Rainfall (6hr): {data['forecast_rainfall']:.1f}mm")
        if 'upstream_sensor_agreement' in data:
            agree = "Yes" if data['upstream_sensor_agreement'] else "No (isolated reading, treat as suspicious)"
            parts.append(f"Upstream Sensor Agreement: {agree}")
        if 'elevation_margin' in data:
            parts.append(f"Elevation Margin Above Danger Line: {data['elevation_margin']:.2f}m")
        if 'evacuation_time_min' in data:
            parts.append(f"Estimated Evacuation Time Available: {data['evacuation_time_min']:.0f}min")
        return f"Flood Sensor Readings: {'; '.join(parts)}"


def create_classifier(onnx_path: Optional[str], model_path: Optional[str], 
                      tokenizer_path: Optional[str], max_length: int):
    """Factory to create best available classifier."""
    if onnx_path and Path(onnx_path).exists():
        return FloodClassifierONNX(onnx_path, tokenizer_path or model_path, max_length)
    elif model_path and Path(model_path).exists():
        return FloodClassifierPyTorch(model_path, max_length)
    else:
        raise FileNotFoundError("No model found. Provide --onnx-path or --model-path")


def main():
    parser = argparse.ArgumentParser(description='Flood risk classification inference')
    parser.add_argument('--onnx-path', type=str, help='Path to ONNX model (recommended for Pi 5)')
    parser.add_argument('--model-path', type=str, help='Path to PyTorch model (LoRA adapters)')
    parser.add_argument('--tokenizer-path', type=str, help='Path to tokenizer (if separate)')
    parser.add_argument('--max-length', type=int, default=256, help='Max sequence length')
    
    # Input options
    parser.add_argument('--water-level', type=float, help='Water level (meters)')
    parser.add_argument('--rainfall', type=float, help='Rainfall 1hr (mm)')
    parser.add_argument('--flow-rate', type=float, help='Flow rate (m³/s)')
    parser.add_argument('--soil-moisture', type=float, help='Soil moisture (%)')
    parser.add_argument('--river-level', type=float, help='River level (meters)')
    parser.add_argument('--forecast-rainfall', type=float, help='Forecast rainfall 6hr (mm)')
    parser.add_argument('--rate-of-rise', type=float, help='Water level rate of rise (m/hr)')
    parser.add_argument('--predicted-water-level-2hr', type=float, help='Predicted water level in 2hr (m)')
    parser.add_argument('--upstream-rainfall-6hr', type=float, help='Upstream rainfall, 6hr rolling (mm)')
    parser.add_argument('--antecedent-precip-index', type=float, help='Antecedent precipitation index')
    parser.add_argument('--elevation-margin', type=float, help='Elevation margin above local danger line (m)')
    parser.add_argument('--evacuation-time-min', type=float, help='Estimated evacuation time available (min)')
    parser.add_argument('--upstream-sensor-agreement', type=str, choices=['yes', 'no'],
                        help='Do 2+ trusted upstream sensors agree on this reading?')
    parser.add_argument('--input-json', type=str, help='JSON file with sensor readings')
    parser.add_argument('--batch-json', type=str, help='JSON file with multiple readings')
    
    # Output
    parser.add_argument('--output-json', type=str, help='Save results to JSON')
    parser.add_argument('--quiet', action='store_true', help='Only output prediction')
    
    args = parser.parse_args()
    
    # Build sensor data
    if args.input_json:
        with open(args.input_json, 'r') as f:
            sensor_data = json.load(f)
    elif args.batch_json:
        with open(args.batch_json, 'r') as f:
            batch_data = json.load(f)
        sensor_data = None  # Will process batch
    else:
        sensor_data = {}
        if args.water_level is not None:
            sensor_data['water_level'] = args.water_level
        if args.rainfall is not None:
            sensor_data['rainfall'] = args.rainfall
        if args.flow_rate is not None:
            sensor_data['flow_rate'] = args.flow_rate
        if args.soil_moisture is not None:
            sensor_data['soil_moisture'] = args.soil_moisture
        if args.river_level is not None:
            sensor_data['river_level'] = args.river_level
        if args.forecast_rainfall is not None:
            sensor_data['forecast_rainfall'] = args.forecast_rainfall
        if args.rate_of_rise is not None:
            sensor_data['rate_of_rise'] = args.rate_of_rise
        if args.predicted_water_level_2hr is not None:
            sensor_data['predicted_water_level_2hr'] = args.predicted_water_level_2hr
        if args.upstream_rainfall_6hr is not None:
            sensor_data['upstream_rainfall_6hr'] = args.upstream_rainfall_6hr
        if args.antecedent_precip_index is not None:
            sensor_data['antecedent_precip_index'] = args.antecedent_precip_index
        if args.elevation_margin is not None:
            sensor_data['elevation_margin'] = args.elevation_margin
        if args.evacuation_time_min is not None:
            sensor_data['evacuation_time_min'] = args.evacuation_time_min
        if args.upstream_sensor_agreement is not None:
            sensor_data['upstream_sensor_agreement'] = (args.upstream_sensor_agreement == 'yes')
        
        if not sensor_data:
            parser.error("Provide sensor readings via args or --input-json/--batch-json")
    
    # Create classifier
    classifier = create_classifier(
        args.onnx_path, args.model_path, args.tokenizer_path, args.max_length
    )
    
    # Run inference
    if args.batch_json:
        results = []
        for i, data in enumerate(batch_data):
            label, conf, probs = classifier.predict(data)
            results.append({
                'index': i,
                'input': data,
                'prediction': label,
                'confidence': conf,
                'probabilities': probs,
            })
            if not args.quiet:
                print(f"[{i}] {label} (conf: {conf:.3f})")
        
        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(results, f, indent=2)
    else:
        label, confidence, probs = classifier.predict(sensor_data)
        
        if args.quiet:
            print(label)
        else:
            print(f"\nPrediction: {label}")
            print(f"Confidence: {confidence:.4f}")
            print("\nAll probabilities:")
            for lbl, prob in probs.items():
                bar = '█' * int(prob * 20)
                print(f"  {lbl:12s}: {prob:.4f} {bar}")
        
        if args.output_json:
            result = {
                'input': sensor_data,
                'prediction': label,
                'confidence': confidence,
                'probabilities': probs,
            }
            with open(args.output_json, 'w') as f:
                json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()

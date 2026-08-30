# Flood Risk Classifier - Qwen2.5-1.5B QLoRA on Raspberry Pi 5

4-class flood risk classification: **NORMAL**, **LOW-ALERT**, **HIGH-ALERT**, **PANIC**

Optimized for Raspberry Pi 5 8GB using QLoRA (4-bit quantization + LoRA) + ONNX export.

---

## Quick Start

### 1. Install Dependencies (on training machine - GPU recommended)
```bash
cd flood_classifier
pip install -r requirements.txt
```

### 2. Generate Synthetic Training Data (replace with real data later)
```bash
python generate_data.py --train-samples 2000 --val-samples 500 --output-dir ./data
```

### 3. Train with QLoRA
```bash
# Find your model path first:
# ls ~/Qwen2.5-1.5B-Instruct  OR  ls ~/.cache/huggingface/hub/models--liudongbo--Qwen2.5-1.5B-Instruct

python train_qlora.py \
  --model-path /path/to/Qwen2.5-1.5B-Instruct \
  --train-data ./data/train.json \
  --val-data ./data/val.json \
  --output-dir ./output \
  --epochs 3 \
  --batch-size 2 \
  --grad-accum 8 \
  --lora-r 16 \
  --lora-alpha 32 \
  --export-onnx \
  --onnx-path ./output/flood_classifier.onnx
```

### 4. Deploy to Raspberry Pi 5

**Copy these files to Pi 5:**
- `output/best_model/` (tokenizer + LoRA adapters) **OR** `output/flood_classifier.onnx`
- `infer.py`
- `requirements_pi.txt` (see below)

**On Pi 5:**
```bash
# Install ONNX Runtime (CPU only, fast on Pi 5)
pip install onnxruntime==1.18.0 transformers==4.41.0 tokenizer

# Or for PyTorch fallback (slower):
pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.41.0 peft==0.11.0
```

**Run inference:**
```bash
# Single prediction (ONNX - recommended)
python infer.py --onnx-path flood_classifier.onnx \
  --water-level 2.5 --rainfall 25 --flow-rate 200 --soil-moisture 70

# Batch prediction
python infer.py --onnx-path flood_classifier.onnx --batch-json sensor_batch.json

# JSON input
python infer.py --onnx-path flood_classifier.onnx --input-json reading.json
```

---

## Model Architecture

| Component | Specification |
|-----------|---------------|
| Base Model | Qwen2.5-1.5B-Instruct (1.5B params) |
| Quantization | 4-bit NF4 (QLoRA) |
| LoRA Rank | 16 (configurable) |
| LoRA Alpha | 32 |
| Target Modules | All attention + MLP projections |
| Classification Head | 4-class (saved with adapters) |
| Max Length | 256 tokens |
| Export | ONNX opset 17 |

---

## Expected JSON Format

**Training/Validation Data:**
```json
[
  {
    "water_level": 2.5,
    "rainfall": 25.0,
    "flow_rate": 200.0,
    "soil_moisture": 70.0,
    "river_level": 4.2,
    "forecast_rainfall": 40.0,
    "label": "HIGH-ALERT",
    "timestamp": "2024-01-15T14:30:00"
  }
]
```

**Required fields:** At least one sensor reading + `label` (NORMAL/LOW-ALERT/HIGH-ALERT/PANIC)

---

## Raspberry Pi 5 Performance

| Backend | Latency (CPU) | Memory | Notes |
|---------|--------------|--------|-------|
| ONNX (CPUExecutionProvider) | ~150-300ms | ~1.5 GB | **Recommended** |
| PyTorch (CPU, FP32) | ~800-1500ms | ~3 GB | Fallback only |
| PyTorch (CPU, INT8) | ~400-600ms | ~2 GB | Requires quantization |

**Pi 5 Optimization Tips:**
1. Use ONNX + `onnxruntime` (no PyTorch needed)
2. Set `OMP_NUM_THREADS=4` for inference
3. Disable swap: `sudo dphys-swapfile swapoff && sudo systemctl disable dphys-swapfile`
4. Use `taskset -c 0-3` to pin to performance cores
5. Overclock slightly: add to `/boot/firmware/config.txt`:
   ```
   arm_freq=2400
   over_voltage=6
   ```

---

## Threshold Tuning

Adjust risk thresholds in `generate_data.py` → `THRESHOLDS` dict based on your local conditions:

```python
THRESHOLDS = {
    'water_level': {'normal': 1.0, 'low': 2.0, 'high': 3.0, 'panic': 4.0},  # meters
    'rainfall_1hr': {'normal': 5, 'low': 15, 'high': 30, 'panic': 50},  # mm
    'flow_rate': {'normal': 50, 'low': 150, 'high': 300, 'panic': 500},  # m³/s
    # ... etc
}
```

---

## Troubleshooting

**CUDA OOM during training:**
- Reduce `--batch-size` to 1
- Increase `--grad-accum` to 16
- Reduce `--max-length` to 128

**Model not found:**
```bash
# Find downloaded model
find ~ -name "Qwen2.5-1.5B-Instruct" -type d 2>/dev/null
# Or check HF cache
ls ~/.cache/huggingface/hub/models--liudongbo--Qwen2.5-1.5B-Instruct/snapshots/
```

**ONNX export fails:**
```bash
pip install onnx onnxruntime optimum
# Re-run with --export-onnx
```

**Pi 5 inference slow:**
- Ensure using ONNX, not PyTorch
- Check `htop` - should use all 4 cores
- Verify `onnxruntime` uses CPUExecutionProvider

---

## Files Structure

```
flood_classifier/
├── train_qlora.py       # Main training script (QLoRA)
├── generate_data.py     # Synthetic data generator
├── infer.py             # Pi 5 inference (ONNX + PyTorch)
├── requirements.txt     # Training dependencies
├── data/
│   ├── train.json
│   └── val.json
└── output/
    ├── best_model/      # LoRA adapters + tokenizer + classifier
    ├── flood_classifier.onnx  # Exported ONNX model
    └── training_config.json
```

---

## License

Apache 2.0 (Qwen2.5 base model license applies)
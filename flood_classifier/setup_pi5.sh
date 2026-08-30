#!/bin/bash
# setup_pi5.sh - Run on Raspberry Pi 5 to set up inference environment

set -e

echo "=========================================="
echo "Flood Classifier - Pi 5 Setup"
echo "=========================================="

# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv git

# Create virtual environment
python3 -m venv ~/flood_env
source ~/flood_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install ONNX Runtime (CPU) - optimized for Pi 5
pip install onnxruntime==1.18.0

# Install tokenizers (Rust-based, fast)
pip install tokenizers==0.19.0

# Install numpy
pip install numpy==1.26.0

# Optional: Install transformers + PyTorch for PyTorch fallback
# Uncomment if needed:
# pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
# pip install transformers==4.41.0 peft==0.11.0

# Performance optimizations
echo "Setting up performance optimizations..."

# Disable swap (improves latency consistency)
sudo dphys-swapfile swapoff 2>/dev/null || true
sudo systemctl disable dphys-swapfile 2>/dev/null || true

# Set CPU governor to performance
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true

# Create inference script wrapper
cat > ~/flood_env/bin/flood-predict << 'EOF'
#!/bin/bash
source ~/flood_env/bin/activate
export OMP_NUM_THREADS=4
export ONNXRUNTIME_NUM_THREADS=4
cd ~/flood_classifier
python infer.py "$@"
EOF
chmod +x ~/flood_env/bin/flood-predict

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To use:"
echo "  1. Copy your model files to ~/flood_classifier/"
echo "  2. Activate environment: source ~/flood_env/bin/activate"
echo "  3. Run prediction:"
echo "     flood-predict --onnx-path flood_classifier.onnx --water-level 2.5 --rainfall 25"
echo ""
echo "Or add to ~/.bashrc:"
echo "  export PATH=\$PATH:~/flood_env/bin"
echo "  alias flood-predict='source ~/flood_env/bin/activate && python ~/flood_classifier/infer.py'"
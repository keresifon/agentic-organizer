# Local Transformer Setup Guide for Mac Mini (M1, 8GB RAM)

## ✅ Your System
- **Chip:** Apple M1 (excellent for ML workloads!)
- **RAM:** 8GB (sufficient for local transformers)
- **Advantage:** Apple Silicon has Metal acceleration for PyTorch

## Step-by-Step Setup

### Step 1: Install Core Dependencies

First, install the base requirements:

```bash
cd /Volumes/Drive/Projects/agentic-organizer
pip3 install -r requirements.txt
```

### Step 2: Install Transformers and PyTorch

For Apple Silicon (M1/M2/M3), PyTorch will automatically use Metal acceleration:

```bash
pip3 install transformers torch
```

**Note:** PyTorch will automatically detect your M1 chip and use Metal Performance Shaders (MPS) for GPU acceleration.

### Step 3: Create .env Configuration File

Create a `.env` file in the project root:

```bash
cd /Volumes/Drive/Projects/agentic-organizer
cat > .env << 'EOF'
# Local Transformer Configuration for Mac Mini (8GB RAM)
# Using Qwen2.5-0.5B-Instruct - optimized for 8GB systems
HUGGINGFACE_MODEL=Qwen/Qwen2.5-0.5B-Instruct
EOF
```

Or manually create `.env` with this content:
```
HUGGINGFACE_MODEL=Qwen/Qwen2.5-0.5B-Instruct
```

### Step 4: Test the Setup

Run a dry-run test to verify everything works:

```bash
python3 main.py --dry-run --scan Downloads
```

**What to expect:**
- First run: Model will download (~1 GB) - this happens automatically
- Model load time: 5-10 seconds
- Categorization: ~1-2 seconds per batch of 20 files
- You should see "Using Apple Silicon (Metal) acceleration" message

## Model Options

### Recommended: Qwen/Qwen2.5-0.5B-Instruct (Default)
- **Size:** ~1 GB download
- **RAM Usage:** ~2-3 GB
- **Speed:** Fast on M1
- **Quality:** Good for file categorization
- **Best for:** 8GB systems

### Alternative: microsoft/Phi-3-mini-4k-instruct
If you want better categorization quality:

```bash
# In .env file:
HUGGINGFACE_MODEL=microsoft/Phi-3-mini-4k-instruct
```

- **Size:** ~2 GB download
- **RAM Usage:** ~4 GB
- **Speed:** Slower but still good
- **Quality:** Better categorization
- **Note:** Tighter on 8GB systems, close other apps when using

## How It Works

1. **Auto-Detection:** The code automatically detects:
   - Your M1 chip → Uses Metal acceleration
   - Local model availability → Uses local instead of API
   - Model from `.env` → Loads your specified model

2. **First Run:** 
   - Downloads model from Hugging Face (one-time)
   - Saves to `~/.cache/huggingface/hub/`
   - Subsequent runs are instant

3. **Performance:**
   - Uses Apple's Neural Engine when possible
   - Metal GPU acceleration for faster inference
   - Unified memory is more efficient than traditional RAM

## Troubleshooting

### "Out of memory" errors
**Solution:**
1. Use `Qwen/Qwen2.5-0.5B-Instruct` (smaller model)
2. Close other applications
3. Restart your Mac Mini

### Model download fails
**Solution:**
1. Check internet connection
2. Ensure ~5GB free disk space
3. Try downloading manually from [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)

### Slow performance
**Solution:**
1. Verify Metal is being used (check console output)
2. Ensure you're using the smaller model
3. Close other apps to free memory

### "transformers not installed" error
**Solution:**
```bash
pip3 install transformers torch
```

## Verification Commands

Check if everything is set up correctly:

```bash
# Check Python packages
python3 -c "import transformers; print('✓ transformers:', transformers.__version__)"
python3 -c "import torch; print('✓ torch:', torch.__version__); print('✓ MPS available:', torch.backends.mps.is_available())"

# Check .env file
cat .env

# Test the categorizer
python3 -c "from categorizer import FileCategorizer; c = FileCategorizer(); print('✓ Categorizer initialized successfully')"
```

## Expected Performance

**With Qwen/Qwen2.5-0.5B-Instruct on M1 Mac Mini:**
- Model load: 5-10 seconds (first time only)
- 100 files: ~15-30 seconds total
- 1000 files: ~3-4 minutes total
- RAM usage: ~3-4 GB total

## Next Steps

Once setup is complete:

1. **Test with dry-run:**
   ```bash
   python3 main.py --dry-run --scan Downloads
   ```

2. **Run interactive organization:**
   ```bash
   python3 main.py --interactive --scan Downloads Desktop
   ```

3. **Set up scheduled runs:**
   ```bash
   python3 main.py --schedule daily --scan Downloads
   ```

## Summary

✅ **Your M1 Mac Mini is perfect for local transformers!**

- Apple Silicon accelerates ML workloads
- 8GB RAM is sufficient with the right model
- Metal GPU acceleration works automatically
- Completely free and private (runs locally)

The setup guide in `MAC_MINI_SETUP.md` is accurate and well-configured for your system!


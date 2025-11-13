# Mac Mini Setup Guide (8GB RAM)

## ✅ Yes, Your Mac Mini Can Run Local Transformers!

Your Mac Mini with 8GB RAM is **perfectly capable** of running local transformers for file organization. Here's what you need to know:

## Mac Mini Advantages

**Good news:**
- ✅ **Apple Silicon (M1/M2/M3) is excellent for ML** - If you have an M-series chip, it has a Neural Engine that accelerates ML workloads
- ✅ **8GB unified memory** - More efficient than traditional RAM on Intel Macs
- ✅ **Metal Performance Shaders** - PyTorch can use GPU acceleration on Apple Silicon
- ✅ **Always-on home server** - Perfect for running as a network service

## Recommended Model for 8GB Mac Mini

**Best Choice: `Qwen/Qwen2.5-0.5B-Instruct`**

```bash
# In your .env file:
HUGGINGFACE_MODEL=Qwen/Qwen2.5-0.5B-Instruct
```

**Why this model:**
- ✅ Only ~1 GB download
- ✅ Uses ~2-3 GB RAM (leaves plenty for macOS)
- ✅ Fast on CPU (works great on Apple Silicon)
- ✅ Good quality for file categorization
- ✅ Perfect for 8GB systems

**Alternative (if you want better quality):**
```bash
HUGGINGFACE_MODEL=microsoft/Phi-3-mini-4k-instruct
```
- Uses ~4 GB RAM (tighter on 8GB systems)
- Better categorization quality
- Still works, but may be slower if other apps are running

## Installation Steps for Mac Mini

### 1. Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install transformers and PyTorch (Mac-optimized)
pip install transformers torch
```

**Note:** PyTorch will automatically detect Apple Silicon and use Metal acceleration.

### 2. Configure Model

Create or edit `.env` file:
```bash
# Use the smaller model for 8GB RAM
HUGGINGFACE_MODEL=Qwen/Qwen2.5-0.5B-Instruct
```

### 3. Test It

```bash
python main.py --dry-run --scan Downloads
```

## Performance Expectations on Mac Mini (8GB)

### With Qwen/Qwen2.5-0.5B-Instruct (Recommended)
- **Model load time:** 5-10 seconds
- **Categorization speed:** ~1-2 seconds per batch of 20 files
- **RAM usage:** ~3-4 GB total (model + macOS + app)
- **Disk space:** ~1 GB for model

### With Phi-3-mini (Alternative)
- **Model load time:** 10-15 seconds
- **Categorization speed:** ~2-4 seconds per batch of 20 files
- **RAM usage:** ~5-6 GB total (tighter, but works)
- **Disk space:** ~2 GB for model

## Setting Up as Home Network Service

Since you mentioned using it on your home network, here are options:

### Option 1: Simple Network Share
1. Run the organizer on Mac Mini
2. Share folders via macOS File Sharing
3. Access from other devices on network
4. Run organizer on Mac Mini to organize shared folders

### Option 2: SSH Access
```bash
# From another device on your network:
ssh username@mac-mini-ip-address
cd /path/to/agentic-organizer
python main.py --scan /shared/folder
```

### Option 3: Create a Simple Web Interface (Future Enhancement)
You could set up a Flask/FastAPI server to expose the organizer over HTTP.

## Memory Management Tips for 8GB

1. **Close other apps** when running categorization
2. **Use the smaller model** (Qwen 0.5B) for best performance
3. **Process in smaller batches** - The code already batches files (20 at a time)
4. **Restart after large batches** - Frees up memory
5. **Monitor Activity Monitor** - Check RAM usage during first run

## Troubleshooting

### "Out of memory" errors
**Solution:**
1. Use `Qwen/Qwen2.5-0.5B-Instruct` instead of Phi-3
2. Close other applications
3. Restart your Mac Mini to free memory

### Slow performance
**Solution:**
1. Check if you have Apple Silicon (M1/M2/M3) - it's much faster
2. Ensure PyTorch is using Metal acceleration (it should auto-detect)
3. Use the smaller model

### Model download fails
**Solution:**
1. Check internet connection
2. Try downloading manually from Hugging Face
3. Check disk space (need ~5GB free)

## Apple Silicon Specific Benefits

If your Mac Mini has M1/M2/M3 chip:

- **Metal acceleration** - PyTorch uses GPU automatically
- **Neural Engine** - Some operations can use dedicated ML hardware
- **Unified memory** - More efficient than traditional RAM
- **Better performance** - Often 2-3x faster than Intel Macs for ML

To check your chip:
```bash
system_profiler SPHardwareDataType | grep "Chip"
```

## Recommended Workflow for Home Network

1. **Set up Mac Mini as always-on organizer:**
   ```bash
   # Create a scheduled task
   python main.py --schedule daily --scan /Users/shared/Downloads
   ```

2. **Share folders from other devices:**
   - Use macOS File Sharing or SMB
   - Point organizer to shared network folders

3. **Access from other devices:**
   - SSH into Mac Mini
   - Run organizer remotely
   - Or set up automated scripts

## Real-World Performance

**Example: Organizing 100 files**
- Model load: 5-10 seconds (one time)
- Categorization: ~10-20 seconds total
- **Total time: ~15-30 seconds**

**Example: Organizing 1000 files**
- Model load: 5-10 seconds (one time)
- Categorization: ~2-3 minutes total
- **Total time: ~3-4 minutes**

## Summary

✅ **Your 8GB Mac Mini is perfectly capable!**

**Recommended setup:**
- Model: `Qwen/Qwen2.5-0.5B-Instruct`
- Close other apps when running
- Use as home network file organizer
- Expect ~1-2 seconds per 20 files

**You'll have:**
- ✅ Free, unlimited file organization
- ✅ Complete privacy (all local)
- ✅ Works offline
- ✅ Perfect for home network setup

The 8GB RAM is sufficient, especially with the smaller model. If you have Apple Silicon, it will perform even better!


# Free LLM Setup Guide

This guide shows you how to use the file organizer with **completely free** LLM options from Hugging Face.

## Option 1: Hugging Face Inference API (Easiest - Recommended)

**Pros:**
- ✅ No local installation needed
- ✅ No model download required
- ✅ Works on any machine
- ✅ Free tier: 1000 requests/month

**Setup:**
1. Sign up for a free account at [Hugging Face](https://huggingface.co/join)
2. Get your API token from [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Create a `.env` file:
   ```
   HUGGINGFACE_API_TOKEN=your_token_here
   ```
4. That's it! The agent will automatically use the Inference API.

**Usage:**
```bash
python main.py --scan Downloads
```

## Option 2: Local Hugging Face Model (Completely Free, No Limits)

**Pros:**
- ✅ **Completely free, no API limits** - Use as much as you want, no monthly quotas
- ✅ **Works offline** - No internet needed after initial download
- ✅ **No API key needed** - Just install and run
- ✅ **Your data stays local** - Files never leave your machine, maximum privacy
- ✅ **No rate limits** - Process thousands of files without waiting
- ✅ **No API costs** - Even if you exceed free tiers, you pay nothing
- ✅ **Customizable** - Can use any model from Hugging Face, fine-tune if needed
- ✅ **Consistent performance** - No API slowdowns or downtime
- ✅ **Learning capability** - Can fine-tune on your specific file patterns

**Cons:**
- ⚠️ **Initial download** - Models are 2-7 GB (one-time download, cached after)
- ⚠️ **RAM/VRAM requirements** - Needs 4-8 GB RAM minimum (more for larger models)
- ⚠️ **Slower first run** - Model loads into memory (10-30 seconds)
- ⚠️ **Disk space** - Models take up 2-7 GB on your hard drive
- ⚠️ **Setup complexity** - Need to install PyTorch and transformers
- ⚠️ **GPU recommended** - Much faster with GPU, but works on CPU (slower)
- ⚠️ **Model quality varies** - Smaller free models may be less accurate than paid APIs
- ⚠️ **Memory usage** - Keeps model in RAM while running (can't free memory easily)

**Setup:**
1. Install transformers and PyTorch:
   ```bash
   pip install transformers torch
   ```
2. That's it! No API key needed. The agent will automatically download and use a free model on first run.

**Usage:**
```bash
python main.py --scan Downloads
```

The first run will download the model (this may take a few minutes). Subsequent runs will be faster.

**Recommended Models:**
- `microsoft/Phi-3-mini-4k-instruct` (default) - Small, efficient, ~2GB
- `Qwen/Qwen2.5-0.5B-Instruct` - Very small, fast
- `microsoft/Phi-3-medium-4k-instruct` - Better quality, ~7GB

To use a different model, set in `.env`:
```
HUGGINGFACE_MODEL=microsoft/Phi-3-mini-4k-instruct
```

## Option 3: Rule-Based Only (No LLM)

If you don't want to use any LLM, the agent will still work using rule-based categorization (file extensions, MIME types). It's less intelligent but still functional.

Just run:
```bash
python main.py --scan Downloads
```

## Detailed Comparison

| Feature | HF Inference API | Local Model | Rule-Based |
|---------|------------------|-------------|------------|
| **Setup Difficulty** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Very Easy |
| **Cost** | Free (1000/month) | Free (unlimited) | Free |
| **Speed** | Fast (network) | Medium (CPU) / Fast (GPU) | Very Fast |
| **Intelligence** | High | High (depends on model) | Medium |
| **Offline** | ❌ | ✅ | ✅ |
| **Privacy** | API call (data sent) | ✅ 100% Local | ✅ 100% Local |
| **Rate Limits** | Yes (1000/month free) | ❌ None | ❌ None |
| **Initial Setup** | 2 minutes | 5-10 minutes | Instant |
| **Disk Space** | None | 2-7 GB | None |
| **RAM Usage** | None | 4-8 GB | Minimal |
| **Best For** | Quick setup, occasional use | Heavy use, privacy-focused | Simple categorization |

## Troubleshooting

**"Model is loading" message:**
- This happens on first API request. Wait 10-30 seconds and try again.

**Out of memory errors (local models):**
- Use a smaller model like `Qwen/Qwen2.5-0.5B-Instruct`
- Or use the Inference API instead

**Slow categorization:**
- Use the Inference API for faster results
- Or use a smaller local model

**No API key and don't want to install transformers:**
- The agent will automatically fall back to rule-based categorization
- Still works, just less intelligent


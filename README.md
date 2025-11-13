# AI File Organization Agent

An intelligent file organization agent that automatically categorizes, organizes, and manages your files using AI.

## Features

- 🔍 **Smart Scanning**: Scans specified directories (Downloads, Desktop, etc.)
- 🤖 **AI-Powered Categorization**: Uses LLM to intelligently categorize files
- 📁 **Organized Structure**: Creates and maintains organized folder structures
- 🔄 **Duplicate Detection**: Detects duplicate files and suggests cleanup
- 🧠 **Learning System**: Learns from your feedback and preferences over time
- 📝 **File Naming**: Handles file naming conventions intelligently
- 📅 **Multi-Organization**: Organizes by date, type, project, and more
- ✅ **Safe Operations**: Asks for confirmation before moving files
- ⏰ **Flexible Execution**: Runs on a schedule or on-demand

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your LLM provider (choose one):**
   
   **Option A: Free Hugging Face Inference API (Recommended for free use)**
   Create a `.env` file:
   ```
   HUGGINGFACE_API_TOKEN=your_hf_token_here
   ```
   Get your free token from [Hugging Face](https://huggingface.co/settings/tokens)
   - Free tier available
   - No local model download needed
   
   **Option B: Local Hugging Face Model (Completely free, no API needed)**
   Install additional packages:
   ```bash
   pip install transformers torch
   ```
   No API key needed! The agent will automatically download and use a free model.
   
   **Option C: OpenAI (Paid)**
   Create a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

3. **Run your first organization:**
   ```bash
   python main.py --dry-run --scan Downloads
   ```
   This will preview what would be organized without making changes.

4. **Organize files:**
   ```bash
   python main.py --interactive --scan Downloads Desktop
   ```

## Installation

See Quick Start above for installation steps.

## Usage

### Basic Usage

```bash
python main.py --scan Downloads Desktop
```

Or use the alias:

```bash
python organizer_cli.py --scan Downloads Desktop
```

### Interactive Mode

```bash
python main.py --interactive --scan Downloads Desktop
```

### Schedule Mode

```bash
python main.py --schedule daily --scan Downloads Desktop
```

### Options

- `--scan <dirs...>`: Scan and organize specified directories
- `--interactive`: Run in interactive mode with prompts
- `--schedule <frequency>`: Schedule automatic runs (daily, weekly, hourly)
- `--dry-run`: Preview changes without making them
- `--config <path>`: Use custom config file

## Configuration

The agent learns your preferences and stores them in `preferences.json`. You can also create a `config.json` to customize:

- Default scan directories
- Organization rules
- Folder naming conventions
- File type mappings

## LLM Provider Options

The agent supports multiple LLM providers:

1. **Hugging Face Inference API** (Free tier available)
   - Set `HUGGINGFACE_API_TOKEN` in `.env`
   - No local installation needed
   - Free tier: 1000 requests/month

2. **Local Hugging Face Models** (Completely free)
   - Install: `pip install transformers torch`
   - No API key needed
   - Runs entirely on your machine
   - Recommended models: `microsoft/Phi-3-mini-4k-instruct` (small, efficient)

3. **OpenAI API** (Paid)
   - Set `OPENAI_API_KEY` in `.env`
   - Uses GPT-4o-mini for categorization

The agent auto-detects which provider to use based on what's available. If none are configured, it falls back to rule-based categorization (still works, just less intelligent).

## Safety

- Always asks for confirmation before moving files
- Creates backups of important operations
- Dry-run mode to preview changes
- Detailed logging of all operations


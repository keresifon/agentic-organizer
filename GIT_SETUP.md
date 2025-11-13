# Git Repository Setup Guide

## Quick Setup for GitHub

### Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it: `agentic-organizer` (or any name you prefer)
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Add Remote and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/agentic-organizer.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Alternative: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/agentic-organizer.git
git branch -M main
git push -u origin main
```

## Accessing from Your Mac Mini

### Option 1: Clone the Repository

```bash
# On your Mac Mini
cd ~
git clone https://github.com/YOUR_USERNAME/agentic-organizer.git
cd agentic-organizer
```

### Option 2: If Already Cloned, Pull Updates

```bash
cd agentic-organizer
git pull origin main
```

## Setting Up on Mac Mini

After cloning:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install transformers torch
   ```

2. **Configure for Mac Mini (8GB RAM):**
   Create `.env` file:
   ```bash
   HUGGINGFACE_MODEL=Qwen/Qwen2.5-0.5B-Instruct
   ```

3. **Follow the guide:**
   ```bash
   cat MAC_MINI_SETUP.md
   ```

4. **Test it:**
   ```bash
   python main.py --dry-run --scan Downloads
   ```

## Useful Git Commands

### On Windows (where you're developing):
```bash
# After making changes
git add .
git commit -m "Description of changes"
git push origin main
```

### On Mac Mini (to get updates):
```bash
git pull origin main
```

## Troubleshooting

### "Repository not found"
- Check the repository URL is correct
- Make sure the repository is public, or you're authenticated

### "Permission denied"
- You may need to authenticate with GitHub
- Use: `gh auth login` (if you have GitHub CLI)
- Or set up SSH keys

### "Branch 'main' does not exist"
- Use: `git push -u origin master` instead (if your branch is master)


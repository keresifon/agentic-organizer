# Web Interface Guide

## 🚀 Quick Start

Start the web interface:

```bash
python3 web_app.py
```

The web interface will be available at:
- **Local:** http://localhost:5000
- **Network:** http://YOUR_IP:5000 (accessible from other devices on your network)

## 📋 Features

### 1. **Dashboard**
   - Real-time status updates
   - File count statistics
   - Category overview

### 2. **File Scanning**
   - Enter directories to scan (comma or newline separated)
   - Examples: `Downloads`, `Downloads, Desktop`, `/path/to/folder`
   - Click "Scan Files" to find all files

### 3. **AI Categorization**
   - After scanning, click "Categorize Files"
   - Uses your local transformer model to categorize files
   - Shows categories and file assignments

### 4. **File Organization**
   - Review categorization results
   - Choose organization options:
     - Organize by date
     - Organize by project
   - Click "Organize Files" to move files to organized folders

### 5. **Duplicate Detection**
   - Click "Check Duplicates" to find duplicate files
   - See potential space savings

## 🌐 Network Access

To access from other devices on your network:

1. Find your Mac Mini's IP address:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. Access from another device:
   ```
   http://YOUR_MAC_MINI_IP:5000
   ```

3. For better network access, you can bind to all interfaces (already configured):
   ```bash
   HOST=0.0.0.0 python3 web_app.py
   ```

## ⚙️ Configuration

### Change Port

```bash
PORT=8080 python3 web_app.py
```

### Change Host

```bash
HOST=127.0.0.1 python3 web_app.py  # Local only
HOST=0.0.0.0 python3 web_app.py    # All interfaces (default)
```

## 🎯 Usage Workflow

1. **Initialize** - Click "Initialize" to load the AI model (first time only)
2. **Scan** - Enter directories and click "Scan Files"
3. **Categorize** - Click "Categorize Files" to use AI categorization
4. **Review** - Check the categories and file assignments
5. **Organize** - Click "Organize Files" to move files to organized folders

## 🔒 Security Note

The web interface runs on your local network. For production use, consider:
- Adding authentication
- Using HTTPS
- Restricting network access

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
PORT=8080 python3 web_app.py
```

### Model Not Loading
- Make sure `.env` file exists with `HUGGINGFACE_MODEL` set
- Check that transformers and torch are installed
- Review console output for errors

### Files Not Found
- Use absolute paths: `/Users/username/Downloads`
- Or relative to home: `Downloads`, `Desktop`
- Check directory permissions

## 📱 Mobile Friendly

The web interface is responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

Perfect for accessing your file organizer from anywhere on your network!


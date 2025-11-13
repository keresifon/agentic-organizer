"""
Web Interface for AI File Organization Agent
"""
import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from typing import List, Dict, Optional
import threading
import time

from file_scanner import FileScanner, FileInfo
from categorizer import FileCategorizer
from duplicate_detector import DuplicateDetector
from organizer import FileOrganizer

app = Flask(__name__)
CORS(app)

# Global state
organizer_agent = None
scan_results = {
    "files": [],
    "categorizations": {},
    "duplicates": {},
    "status": "idle",
    "message": "Ready to scan",
    "progress": {
        "current": 0,
        "total": 0,
        "phase": "idle",  # idle, scanning, categorizing, organizing
        "current_file": "",
        "files_found": 0
    }
}


class WebOrganizerAgent:
    """Organizer agent for web interface"""
    
    def __init__(self):
        self.categorizer = None
        self.duplicate_detector = None
        self.organizer = None
        self.initialized = False
    
    def initialize(self):
        """Initialize components"""
        if not self.initialized:
            try:
                self.categorizer = FileCategorizer()
                self.duplicate_detector = DuplicateDetector()
                self.organizer = FileOrganizer()
                self.initialized = True
                return True, "Components initialized successfully"
            except Exception as e:
                return False, f"Error initializing: {str(e)}"
        return True, "Already initialized"
    
    def scan_directories(self, directories: List[str]):
        """Scan directories for files"""
        try:
            scanner = FileScanner(directories, compute_hash=True)
            files = scanner.scan()
            return True, f"Found {len(files)} files", files
        except Exception as e:
            return False, f"Error scanning: {str(e)}", []
    
    def find_duplicates(self, files: List[FileInfo]) -> Dict:
        """Find duplicate files"""
        try:
            duplicates = self.duplicate_detector.find_duplicates(files)
            summary = self.duplicate_detector.get_duplicate_summary()
            return {
                "success": True,
                "duplicates": duplicates,
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duplicates": {},
                "summary": {}
            }
    
    def categorize_files(self, files: List[FileInfo], progress_callback=None):
        """Categorize files using AI"""
        try:
            categorizations = self.categorizer.categorize_files(files, progress_callback=progress_callback)
            return True, "Categorization complete", categorizations
        except Exception as e:
            return False, f"Error categorizing: {str(e)}", {}
    
    def organize_files(
        self,
        files: List[FileInfo],
        categorizations: Dict[FileInfo, Dict],
        organize_by_date: bool = True,
        organize_by_project: bool = True
    ):
        """Organize files into folders"""
        try:
            moved_files = self.organizer.organize_by_category(
                files,
                categorizations,
                organize_by_date=organize_by_date,
                organize_by_project=organize_by_project
            )
            summary = self.organizer.get_organization_summary()
            return True, "Organization complete", summary
        except Exception as e:
            return False, f"Error organizing: {str(e)}", {}


def init_agent():
    """Initialize the organizer agent"""
    global organizer_agent
    if organizer_agent is None:
        organizer_agent = WebOrganizerAgent()
    return organizer_agent.initialize()


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify({
        "status": scan_results["status"],
        "message": scan_results["message"],
        "files_count": len(scan_results["files"]),
        "categorizations_count": len(scan_results["categorizations"]),
        "initialized": organizer_agent.initialized if organizer_agent else False,
        "progress": scan_results.get("progress", {
            "current": 0,
            "total": 0,
            "phase": "idle",
            "current_file": "",
            "files_found": 0
        })
    })


@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the organizer components"""
    success, message = init_agent()
    if success:
        scan_results["status"] = "ready"
        scan_results["message"] = message
    else:
        scan_results["status"] = "error"
        scan_results["message"] = message
    return jsonify({"success": success, "message": message})


@app.route('/api/scan', methods=['POST'])
def scan():
    """Scan directories for files"""
    data = request.json
    directories = data.get("directories", [])
    
    if not directories:
        return jsonify({"success": False, "message": "No directories specified"}), 400
    
    scan_results["status"] = "scanning"
    scan_results["message"] = "Scanning directories..."
    scan_results["progress"] = {
        "current": 0,
        "total": 0,
        "phase": "scanning",
        "current_file": "",
        "files_found": 0
    }
    
    def do_scan():
        global organizer_agent
        if organizer_agent is None or not organizer_agent.initialized:
            success, msg = init_agent()
            if not success:
                scan_results["status"] = "error"
                scan_results["message"] = msg
                scan_results["progress"]["phase"] = "error"
                return
        
        try:
            # Create a custom scanner that reports progress
            from file_scanner import FileScanner
            scanner = FileScanner(directories, compute_hash=True)
            
            # Scan with progress tracking
            files = []
            scan_results["progress"]["phase"] = "scanning"
            scan_results["progress"]["current_file"] = "Starting scan..."
            
            # Use the scanner's scan method but track progress
            for directory in directories:
                scan_results["progress"]["current_file"] = f"Scanning: {directory}"
                dir_path = Path(directory)
                if dir_path.exists() and dir_path.is_dir():
                    # Count files first for progress estimation
                    file_count = sum(1 for _ in dir_path.rglob('*') if _.is_file())
                    scan_results["progress"]["total"] += file_count
            
            # Now do the actual scan
            files = scanner.scan()
            
            scan_results["files"] = [
                {
                    "path": str(f.path),
                    "name": f.name,
                    "size": f.size,
                    "size_mb": round(f.size / (1024 * 1024), 2),
                    "extension": f.extension,
                    "mime_type": f.mime_type,
                    "modified": f.modified.isoformat() if f.modified else None
                }
                for f in files
            ]
            
            scan_results["status"] = "scanned"
            scan_results["message"] = f"Found {len(files)} files"
            scan_results["progress"] = {
                "current": len(files),
                "total": len(files),
                "phase": "complete",
                "current_file": f"Scan complete: {len(files)} files found",
                "files_found": len(files)
            }
        except Exception as e:
            scan_results["status"] = "error"
            scan_results["message"] = f"Error scanning: {str(e)}"
            scan_results["progress"]["phase"] = "error"
    
    thread = threading.Thread(target=do_scan)
    thread.start()
    
    return jsonify({"success": True, "message": "Scan started"})


@app.route('/api/files')
def get_files():
    """Get scanned files"""
    return jsonify({
        "files": scan_results["files"],
        "count": len(scan_results["files"])
    })


@app.route('/api/categorize', methods=['POST'])
def categorize():
    """Categorize files using AI"""
    if not scan_results["files"]:
        return jsonify({"success": False, "message": "No files to categorize. Please scan first."}), 400
    
    scan_results["status"] = "categorizing"
    scan_results["message"] = "Categorizing files with AI..."
    scan_results["progress"] = {
        "current": 0,
        "total": len(scan_results["files"]),
        "phase": "categorizing",
        "current_file": "Starting AI categorization...",
        "files_found": len(scan_results["files"])
    }
    
    def do_categorize():
        global organizer_agent
        # Reconstruct FileInfo objects from stored data
        files = []
        for f_data in scan_results["files"]:
            file_path = Path(f_data["path"])
            if file_path.exists():
                from datetime import datetime
                files.append(FileInfo(
                    path=file_path,
                    name=f_data["name"],
                    size=f_data["size"],
                    extension=f_data["extension"],
                    mime_type=f_data.get("mime_type"),
                    created=datetime.fromtimestamp(file_path.stat().st_ctime),
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime)
                ))
        
        # Progress callback to update scan_results
        def update_progress(current, total, current_file):
            scan_results["progress"]["current"] = current
            scan_results["progress"]["total"] = total
            scan_results["progress"]["current_file"] = current_file
            scan_results["progress"]["phase"] = "categorizing"
            # Calculate percentage for better feedback
            percent = (current / total * 100) if total > 0 else 0
            scan_results["message"] = f"Categorizing: {current:,}/{total:,} files ({percent:.1f}%)"
        
        success, message, categorizations = organizer_agent.categorize_files(files, progress_callback=update_progress)
        
        if success:
            # Convert FileInfo keys to path strings for JSON serialization
            scan_results["categorizations"] = {
                str(f.path): {
                    "category": cat.get("category", "Other"),
                    "subcategory": cat.get("subcategory"),
                    "project": cat.get("project"),
                    "suggested_name": cat.get("suggested_name"),
                    "confidence": cat.get("confidence", 0.0),
                    "reason": cat.get("reason", "")
                }
                for f, cat in categorizations.items()
            }
            scan_results["status"] = "categorized"
            scan_results["message"] = message
            scan_results["progress"] = {
                "current": len(categorizations),
                "total": len(files),
                "phase": "complete",
                "current_file": f"Categorization complete: {len(categorizations)} files",
                "files_found": len(files)
            }
        else:
            scan_results["status"] = "error"
            scan_results["message"] = message
            scan_results["progress"]["phase"] = "error"
    
    thread = threading.Thread(target=do_categorize)
    thread.start()
    
    return jsonify({"success": True, "message": "Categorization started"})


@app.route('/api/categorizations')
def get_categorizations():
    """Get file categorizations"""
    # Combine files with their categorizations
    files_with_cats = []
    for file_data in scan_results["files"]:
        file_path = file_data["path"]
        cat_data = scan_results["categorizations"].get(file_path, {})
        files_with_cats.append({
            **file_data,
            "categorization": cat_data
        })
    
    # Count by category
    category_counts = {}
    for cat_data in scan_results["categorizations"].values():
        category = cat_data.get("category", "Other")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return jsonify({
        "files": files_with_cats,
        "category_counts": category_counts,
        "total": len(files_with_cats)
    })


@app.route('/api/organize', methods=['POST'])
def organize():
    """Organize files into folders"""
    if not scan_results["categorizations"]:
        return jsonify({"success": False, "message": "No categorizations available. Please categorize first."}), 400
    
    data = request.json
    organize_by_date = data.get("organize_by_date", True)
    organize_by_project = data.get("organize_by_project", True)
    
    scan_results["status"] = "organizing"
    scan_results["message"] = "Organizing files..."
    scan_results["progress"] = {
        "current": 0,
        "total": len(scan_results["categorizations"]),
        "phase": "organizing",
        "current_file": "Starting file organization...",
        "files_found": len(scan_results["files"])
    }
    
    def do_organize():
        global organizer_agent
        # Reconstruct FileInfo objects and categorizations
        files = []
        categorizations = {}
        
        for f_data in scan_results["files"]:
            file_path = Path(f_data["path"])
            if file_path.exists():
                from datetime import datetime
                file_info = FileInfo(
                    path=file_path,
                    name=f_data["name"],
                    size=f_data["size"],
                    extension=f_data["extension"],
                    mime_type=f_data.get("mime_type"),
                    created=datetime.fromtimestamp(file_path.stat().st_ctime),
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime)
                )
                files.append(file_info)
                
                # Get categorization for this file
                cat_data = scan_results["categorizations"].get(str(file_path), {})
                categorizations[file_info] = cat_data
        
        success, message, summary = organizer_agent.organize_files(
            files,
            categorizations,
            organize_by_date=organize_by_date,
            organize_by_project=organize_by_project
        )
        
        if success:
            scan_results["status"] = "organized"
            scan_results["message"] = message
            scan_results["organization_summary"] = summary
            scan_results["progress"] = {
                "current": summary.get("successful", 0),
                "total": summary.get("total_files", 0),
                "phase": "complete",
                "current_file": f"Organized {summary.get('successful', 0)} files",
                "files_found": len(scan_results["files"])
            }
        else:
            scan_results["status"] = "error"
            scan_results["message"] = message
            scan_results["progress"]["phase"] = "error"
    
    thread = threading.Thread(target=do_organize)
    thread.start()
    
    return jsonify({"success": True, "message": "Organization started"})


@app.route('/api/duplicates', methods=['POST'])
def find_duplicates():
    """Find duplicate files"""
    if not scan_results["files"]:
        return jsonify({"success": False, "message": "No files to check. Please scan first."}), 400
    
    scan_results["status"] = "checking_duplicates"
    scan_results["message"] = "Checking for duplicates..."
    
    def do_find_duplicates():
        global organizer_agent
        # Reconstruct FileInfo objects
        files = []
        for f_data in scan_results["files"]:
            file_path = Path(f_data["path"])
            if file_path.exists():
                from datetime import datetime
                files.append(FileInfo(
                    path=file_path,
                    name=f_data["name"],
                    size=f_data["size"],
                    extension=f_data["extension"],
                    mime_type=f_data.get("mime_type"),
                    created=datetime.fromtimestamp(file_path.stat().st_ctime),
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                    hash=f_data.get("hash")
                ))
        
        result = organizer_agent.find_duplicates(files)
        scan_results["duplicates"] = result
        
        if result["success"]:
            scan_results["status"] = "duplicates_found"
            scan_results["message"] = f"Found {result['summary'].get('duplicate_groups', 0)} duplicate groups"
        else:
            scan_results["status"] = "error"
            scan_results["message"] = result.get("error", "Error finding duplicates")
    
    thread = threading.Thread(target=do_find_duplicates)
    thread.start()
    
    return jsonify({"success": True, "message": "Duplicate check started"})


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset scan results"""
    scan_results["files"] = []
    scan_results["categorizations"] = {}
    scan_results["duplicates"] = {}
    scan_results["status"] = "idle"
    scan_results["message"] = "Ready to scan"
    return jsonify({"success": True, "message": "Reset complete"})


@app.route('/api/browse', methods=['GET'])
def browse_directory():
    """Browse filesystem directories"""
    path = request.args.get('path', '/')
    
    # Security: prevent directory traversal
    try:
        path_obj = Path(path).resolve()
        home = Path.home()
        
        # Allow browsing:
        # 1. Home directory and subdirectories
        # 2. /Volumes (external drives on macOS)
        # 3. /Users (other user directories)
        # 4. Direct paths that exist and are accessible
        
        path_str = str(path_obj)
        is_allowed = (
            path_str.startswith(str(home)) or
            path_str.startswith('/Volumes') or
            path_str.startswith('/Users')
        )
        
        # If path is not in allowed areas, check if it's a direct volume mount
        if not is_allowed:
            # Check if it's a direct path to an existing directory (for external drives)
            if path_obj.exists() and path_obj.is_dir():
                # Allow if it's a direct child of /Volumes or accessible
                try:
                    # Check if we can access it
                    list(path_obj.iterdir())
                    is_allowed = True
                except PermissionError:
                    is_allowed = False
            else:
                is_allowed = False
        
        if not is_allowed:
            # Default to home if path is not allowed
            path_obj = home
        elif not path_obj.exists() or not path_obj.is_dir():
            path_obj = home
        
        items = []
        try:
            for item in sorted(path_obj.iterdir()):
                try:
                    # Skip hidden files/folders (except .)
                    if item.name.startswith('.') and item.name != '.':
                        continue
                    
                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "is_directory": item.is_dir(),
                        "is_file": item.is_file(),
                    }
                    
                    if item.is_file():
                        try:
                            stat = item.stat()
                            item_info["size"] = stat.st_size
                            item_info["size_mb"] = round(stat.st_size / (1024 * 1024), 2)
                        except:
                            pass
                    
                    items.append(item_info)
                except PermissionError:
                    continue
                except Exception:
                    continue
        
        except PermissionError:
            return jsonify({"success": False, "message": "Permission denied", "items": [], "current_path": str(path_obj)}), 403
        
        return jsonify({
            "success": True,
            "items": items,
            "current_path": str(path_obj),
            "parent_path": str(path_obj.parent) if path_obj.parent != path_obj else None
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "items": [], "current_path": "/"}), 500


@app.route('/api/common-directories', methods=['GET'])
def get_common_directories():
    """Get common directory paths"""
    home = Path.home()
    common_dirs = []
    
    common_paths = [
        ("Home", str(home)),
        ("Downloads", str(home / "Downloads")),
        ("Desktop", str(home / "Desktop")),
        ("Documents", str(home / "Documents")),
        ("Pictures", str(home / "Pictures")),
        ("Videos", str(home / "Videos")),
        ("Music", str(home / "Music")),
    ]
    
    for name, path in common_paths:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_dir():
            common_dirs.append({"name": name, "path": path})
    
    # Add Volumes if it exists (for external drives on macOS)
    volumes = Path("/Volumes")
    if volumes.exists() and volumes.is_dir():
        try:
            for vol in sorted(volumes.iterdir()):
                # Skip symlinks and hidden items
                if vol.name.startswith('.') or vol.is_symlink():
                    continue
                
                if vol.is_dir():
                    try:
                        # Verify we can access it by trying to list contents
                        list(vol.iterdir())
                        # Add external drive with a clear label
                        vol_name = vol.name
                        # Check if it's the main external drive (Drive)
                        if vol_name == "Drive":
                            common_dirs.append({"name": f"💾 External Drive ({vol_name})", "path": str(vol)})
                        else:
                            common_dirs.append({"name": f"📀 {vol_name}", "path": str(vol)})
                    except (PermissionError, OSError) as e:
                        # Skip if we can't access it
                        print(f"Cannot access volume {vol.name}: {e}")
                        continue
        except Exception as e:
            print(f"Error listing volumes: {e}")
            pass
    
    return jsonify({"success": True, "directories": common_dirs})


if __name__ == '__main__':
    # Initialize agent on startup
    init_agent()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"\n🚀 Starting File Organizer Web Interface...")
    print(f"📡 Access at: http://localhost:{port}")
    print(f"🌐 Network access: http://{host}:{port}")
    print(f"Press Ctrl+C to stop\n")
    
    app.run(host=host, port=port, debug=True, threaded=True)


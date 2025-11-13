"""
File Scanner Module - Scans directories and collects file information
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import filetype


@dataclass(frozen=True)
class FileInfo:
    """Information about a file"""
    path: Path
    name: str
    size: int
    extension: str
    mime_type: Optional[str]
    created: datetime
    modified: datetime
    hash: Optional[str] = None
    category: Optional[str] = None
    project: Optional[str] = None


class FileScanner:
    """Scans directories and collects file information"""
    
    def __init__(self, directories: List[str], compute_hash: bool = False):
        self.directories = [Path(d) for d in directories]
        self.compute_hash = compute_hash
        self.scanned_files: List[FileInfo] = []
    
    def scan(self) -> List[FileInfo]:
        """Scan all specified directories and return file information"""
        self.scanned_files = []
        
        for directory in self.directories:
            if not directory.exists():
                print(f"Warning: Directory {directory} does not exist, skipping...")
                continue
            
            for file_path in self._walk_directory(directory):
                try:
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        self.scanned_files.append(file_info)
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
        
        return self.scanned_files
    
    def _walk_directory(self, directory: Path):
        """Walk through directory and yield file paths"""
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    # Skip hidden files
                    if not file.startswith('.'):
                        yield Path(root) / file
        except PermissionError:
            print(f"Permission denied: {directory}")
    
    def _get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """Get information about a file"""
        try:
            stat = file_path.stat()
            
            # Get MIME type
            mime_type = None
            try:
                kind = filetype.guess(str(file_path))
                if kind:
                    mime_type = kind.mime
            except:
                pass
            
            # Compute hash if requested
            file_hash = None
            if self.compute_hash:
                file_hash = self._compute_hash(file_path)
            
            return FileInfo(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                extension=file_path.suffix.lower(),
                mime_type=mime_type,
                created=datetime.fromtimestamp(stat.st_ctime),
                modified=datetime.fromtimestamp(stat.st_mtime),
                hash=file_hash
            )
        except Exception as e:
            print(f"Error getting info for {file_path}: {e}")
            return None
    
    def _compute_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Compute MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return ""


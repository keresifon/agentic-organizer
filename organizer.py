"""
File Organizer - Organizes files into structured folders
"""
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from file_scanner import FileInfo
from categorizer import FileCategorizer


class FileOrganizer:
    """Organizes files into structured folder hierarchies"""
    
    def __init__(self, base_organize_dir: Optional[Path] = None):
        self.base_organize_dir = base_organize_dir or Path.home() / "OrganizedFiles"
        self.organize_dir = self.base_organize_dir
        self.moved_files: List[Dict] = []
    
    def organize_by_category(
        self,
        files: List[FileInfo],
        categorizations: Dict[FileInfo, Dict],
        organize_by_date: bool = False,
        organize_by_project: bool = False
    ) -> List[Dict]:
        """Organize files based on categorization"""
        self.moved_files = []
        
        # Group files by category
        category_groups: Dict[str, List[tuple]] = {}
        for file, cat_info in categorizations.items():
            category = cat_info.get("category", "Other")
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append((file, cat_info))
        
        # Create folder structure and move files
        for category, file_list in category_groups.items():
            category_path = self.organize_dir / category
            category_path.mkdir(parents=True, exist_ok=True)
            
            for file, cat_info in file_list:
                # Determine destination path
                dest_path = self._determine_destination(file, cat_info, category_path, organize_by_date, organize_by_project)
                
                # Move file
                move_info = self._move_file(file.path, dest_path, cat_info.get("suggested_name"))
                if move_info:
                    self.moved_files.append(move_info)
        
        return self.moved_files
    
    def _determine_destination(
        self,
        file: FileInfo,
        cat_info: Dict,
        category_path: Path,
        organize_by_date: bool,
        organize_by_project: bool
    ) -> Path:
        """Determine the destination path for a file"""
        dest_path = category_path
        
        # Add project subfolder if applicable
        if organize_by_project and cat_info.get("project"):
            project_name = self._sanitize_name(cat_info["project"])
            dest_path = dest_path / project_name
            dest_path.mkdir(parents=True, exist_ok=True)
        
        # Add date subfolder if applicable
        if organize_by_date:
            date_folder = file.modified.strftime("%Y-%m")
            dest_path = dest_path / date_folder
            dest_path.mkdir(parents=True, exist_ok=True)
        
        # Add subcategory folder if applicable
        if cat_info.get("subcategory"):
            subcat_name = self._sanitize_name(cat_info["subcategory"])
            dest_path = dest_path / subcat_name
            dest_path.mkdir(parents=True, exist_ok=True)
        
        return dest_path
    
    def _move_file(self, source: Path, dest_dir: Path, suggested_name: Optional[str] = None) -> Optional[Dict]:
        """Move a file to destination directory"""
        try:
            # Use suggested name if provided, otherwise keep original name
            dest_name = suggested_name if suggested_name else source.name
            dest_name = self._sanitize_name(dest_name)
            dest_path = dest_dir / dest_name
            
            # Handle name conflicts
            if dest_path.exists():
                # Add number suffix
                stem = dest_path.stem
                suffix = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            # Move file
            shutil.move(str(source), str(dest_path))
            
            return {
                "source": str(source),
                "destination": str(dest_path),
                "success": True
            }
        except Exception as e:
            print(f"Error moving {source} to {dest_dir}: {e}")
            return {
                "source": str(source),
                "destination": str(dest_dir),
                "success": False,
                "error": str(e)
            }
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize file/folder name to be filesystem-safe"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        name = name.strip(' .')
        
        # Limit length
        if len(name) > 200:
            name = name[:200]
        
        return name
    
    def create_folder_structure(self, categories: List[str]):
        """Create base folder structure"""
        self.organize_dir.mkdir(parents=True, exist_ok=True)
        
        for category in categories:
            category_path = self.organize_dir / category
            category_path.mkdir(parents=True, exist_ok=True)
    
    def get_organization_summary(self) -> Dict:
        """Get summary of organization operations"""
        successful = sum(1 for m in self.moved_files if m.get("success", False))
        failed = len(self.moved_files) - successful
        
        return {
            "total_files": len(self.moved_files),
            "successful": successful,
            "failed": failed,
            "organize_directory": str(self.organize_dir)
        }

"""
Duplicate File Detector - Detects duplicate files and suggests cleanup
"""
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from file_scanner import FileInfo


class DuplicateDetector:
    """Detects duplicate files using hash comparison"""
    
    def __init__(self):
        self.duplicates: Dict[str, List[FileInfo]] = {}
    
    def find_duplicates(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """Find duplicate files based on hash"""
        # Group files by hash
        hash_groups: Dict[str, List[FileInfo]] = defaultdict(list)
        
        for file in files:
            if file.hash:
                hash_groups[file.hash].append(file)
        
        # Find groups with more than one file (duplicates)
        duplicates = {}
        for file_hash, file_list in hash_groups.items():
            if len(file_list) > 1:
                duplicates[file_hash] = file_list
        
        self.duplicates = duplicates
        return duplicates
    
    def find_similar_names(self, files: List[FileInfo]) -> List[List[FileInfo]]:
        """Find files with similar names (potential duplicates)"""
        name_groups: Dict[str, List[FileInfo]] = defaultdict(list)
        
        # Normalize names (lowercase, remove special chars)
        for file in files:
            normalized = self._normalize_name(file.name)
            name_groups[normalized].append(file)
        
        # Return groups with multiple files
        similar = []
        for normalized, file_list in name_groups.items():
            if len(file_list) > 1:
                similar.append(file_list)
        
        return similar
    
    def _normalize_name(self, name: str) -> str:
        """Normalize file name for comparison"""
        # Remove extension, lowercase, remove special chars
        name_without_ext = Path(name).stem.lower()
        # Remove common variations
        name_without_ext = name_without_ext.replace('copy', '').replace('_', '').replace('-', '')
        name_without_ext = ''.join(c for c in name_without_ext if c.isalnum())
        return name_without_ext
    
    def suggest_cleanup(self, duplicates: Dict[str, List[FileInfo]]) -> List[Dict]:
        """Suggest which files to keep and which to delete"""
        suggestions = []
        
        for file_hash, file_list in duplicates.items():
            # Sort by: 1) path depth (prefer files in organized folders), 2) modification date (newer is better)
            sorted_files = sorted(
                file_list,
                key=lambda f: (
                    -len(f.path.parts),  # Prefer files in deeper directories (more organized)
                    f.modified  # Then by modification date (newer first)
                )
            )
            
            # Keep the first one (best candidate)
            keep = sorted_files[0]
            remove = sorted_files[1:]
            
            suggestions.append({
                "keep": keep,
                "remove": remove,
                "reason": f"Keep {keep.path} (most organized location, modified {keep.modified.strftime('%Y-%m-%d')})"
            })
        
        return suggestions
    
    def get_duplicate_summary(self) -> Dict:
        """Get summary of duplicate files"""
        total_duplicates = sum(len(files) - 1 for files in self.duplicates.values())
        total_size = 0
        
        for file_list in self.duplicates.values():
            # Size of duplicates (excluding the one to keep)
            for file in file_list[1:]:
                total_size += file.size
        
        return {
            "duplicate_groups": len(self.duplicates),
            "total_duplicate_files": total_duplicates,
            "total_wasted_space_mb": round(total_size / (1024 * 1024), 2),
            "total_wasted_space_gb": round(total_size / (1024 * 1024 * 1024), 2)
        }


import os
import time
import threading
import logging
from datetime import datetime, timedelta

class FileManager:
    """Manages downloaded files and cleanup operations"""
    
    def __init__(self, downloads_dir='downloads', max_age_minutes=15):
        self.downloads_dir = downloads_dir
        self.max_age_minutes = max_age_minutes
        self.cleanup_interval = 300  # 5 minutes
        
        # Ensure downloads directory exists
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def cleanup_old_files(self):
        """Background thread to clean up old files"""
        while True:
            try:
                self._cleanup_files()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logging.error(f"Cleanup error: {str(e)}")
                time.sleep(self.cleanup_interval)
    
    def _cleanup_files(self):
        """Remove files older than max_age_minutes"""
        if not os.path.exists(self.downloads_dir):
            return
        
        current_time = time.time()
        cutoff_time = current_time - (self.max_age_minutes * 60)
        
        for filename in os.listdir(self.downloads_dir):
            if filename == '.gitkeep':
                continue
                
            file_path = os.path.join(self.downloads_dir, filename)
            
            try:
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        logging.info(f"Cleaned up old file: {filename}")
                        
            except Exception as e:
                logging.error(f"Error cleaning up {filename}: {str(e)}")
    
    def find_latest_download(self):
        """Find the most recently downloaded file"""
        if not os.path.exists(self.downloads_dir):
            return None
        
        files = []
        for filename in os.listdir(self.downloads_dir):
            if filename == '.gitkeep':
                continue
                
            file_path = os.path.join(self.downloads_dir, filename)
            if os.path.isfile(file_path):
                mtime = os.path.getmtime(file_path)
                files.append((file_path, mtime))
        
        if not files:
            return None
        
        # Return the most recent file
        latest_file = max(files, key=lambda x: x[1])
        return latest_file[0]
    
    def get_recent_downloads(self, limit=5):
        """Get list of recent downloads for display"""
        if not os.path.exists(self.downloads_dir):
            return []
        
        files = []
        for filename in os.listdir(self.downloads_dir):
            if filename == '.gitkeep':
                continue
                
            file_path = os.path.join(self.downloads_dir, filename)
            if os.path.isfile(file_path):
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                files.append({
                    'filename': filename,
                    'size': self._format_file_size(size),
                    'timestamp': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by modification time (newest first) and limit
        files.sort(key=lambda x: x['timestamp'], reverse=True)
        return files[:limit]
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_file_path(self, filename):
        """Get full path for a filename"""
        return os.path.join(self.downloads_dir, filename)
    
    def file_exists(self, filename):
        """Check if a file exists in downloads directory"""
        return os.path.exists(self.get_file_path(filename))

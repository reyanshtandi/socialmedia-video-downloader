import os
import time
import threading
import logging

def cleanup_old_files():
    """
    Background thread to clean up old downloaded files
    Runs every 5 minutes and removes files older than 15 minutes
    """
    while True:
        try:
            cleanup_downloads_folder()
            time.sleep(300)  # Wait 5 minutes
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}")
            time.sleep(60)  # Wait 1 minute on error

def cleanup_downloads_folder():
    """
    Remove files older than 15 minutes from downloads folder
    """
    downloads_dir = 'downloads'
    current_time = time.time()
    max_age = 15 * 60  # 15 minutes in seconds
    
    if not os.path.exists(downloads_dir):
        return
    
    for filename in os.listdir(downloads_dir):
        if filename == '.gitkeep':
            continue
            
        file_path = os.path.join(downloads_dir, filename)
        
        try:
            # Check if file is older than max_age
            file_age = current_time - os.path.getctime(file_path)
            
            if file_age > max_age:
                os.remove(file_path)
                logging.info(f"Cleaned up old file: {filename}")
                
        except Exception as e:
            logging.error(f"Error cleaning up file {filename}: {str(e)}")

def manual_cleanup():
    """
    Manual cleanup function that can be called from routes
    """
    cleanup_downloads_folder()

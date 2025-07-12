# SocialNetworkPro

A full-featured backend downloader project built with Flask and yt-dlp, capable of downloading videos from social media platforms like YouTube, Instagram, and more.

## 🚀 Features

- URL detection for different platforms
- File management and cleanup
- Download handling with yt-dlp
- Simple Flask web interface

## 📁 Project Structure

- `app.py` / `main.py` – Main Flask application
- `cleanup.py` – Handles post-download cleanup
- `file_manager.py` – Manages download storage
- `platform_detector.py` – Detects source platforms
- `templates/` – HTML interface
- `static/` – CSS/JS for frontend
- `downloads/` – Stores downloaded files

## 🛠 How to Run Locally

```bash
pip install -r requirements.txt
python app.py
# or
gunicorn app:app

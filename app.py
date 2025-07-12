import os
import logging
import threading
import time
import json
from urllib.parse import urlparse
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from platform_detector import detect_platform
from cleanup import cleanup_old_files
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)

# Create downloads directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

# Import models after app and db initialization
from models import create_models
Download, Newsletter, Analytics, ErrorLog = create_models(db)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Get recent downloads from database
    recent_downloads = Download.query.filter_by(status='completed').order_by(Download.completed_at.desc()).limit(3).all()
    return render_template('index.html', recent_downloads=recent_downloads)

@app.route('/detect', methods=['POST'])
def detect():
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Please enter a valid URL', 'error')
        return redirect(url_for('index'))
    
    platform = detect_platform(url)
    
    if platform == 'unknown':
        flash('Unsupported platform. Please check the URL and try again.', 'error')
        return redirect(url_for('index'))
    
    # Log the detection event
    try:
        analytics = Analytics(
            event_type='url_detection',
            platform=platform,
            url=url,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(analytics)
        db.session.commit()
    except Exception as e:
        logging.error(f"Analytics error: {str(e)}")
    
    return redirect(url_for(f'{platform}_page', url=url))

@app.route('/youtube')
def youtube_page():
    url = request.args.get('url', '')
    return render_template('youtube.html', url=url)

@app.route('/instagram')
def instagram_page():
    url = request.args.get('url', '')
    return render_template('instagram.html', url=url)

@app.route('/tiktok')
def tiktok_page():
    url = request.args.get('url', '')
    return render_template('tiktok.html', url=url)

@app.route('/twitter')
def twitter_page():
    url = request.args.get('url', '')
    return render_template('twitter.html', url=url)

@app.route('/facebook')
def facebook_page():
    url = request.args.get('url', '')
    return render_template('facebook.html', url=url)

@app.route('/download')
def download_media():
    url = request.args.get('url', '')
    audio_only = request.args.get('audio_only', 'false').lower() == 'true'
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    platform = detect_platform(url)
    download_record = None
    
    try:
        # Create download record
        download_record = Download(
            url=url,
            platform=platform,
            download_type='audio' if audio_only else 'video',
            status='pending',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(download_record)
        db.session.commit()
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'mp3/bestaudio/best' if audio_only else 'best',
            'extractaudio': audio_only,
            'audioformat': 'mp3' if audio_only else None,
            'noplaylist': True,
            'writeinfojson': False,
            'writedescription': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        # Add platform-specific options
        if platform == 'youtube' and audio_only:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            uploader = info.get('uploader', 'Unknown')
            duration = info.get('duration', 0)
            view_count = info.get('view_count', 0)
            
            # Update download record with metadata
            download_record.title = title
            download_record.uploader = uploader
            download_record.duration = duration
            download_record.view_count = view_count
            
            # Download the media
            ydl.download([url])
            
            # Find the downloaded file
            downloaded_file = None
            for file in os.listdir('downloads'):
                if file.startswith(title[:50]) or title[:50] in file:
                    downloaded_file = file
                    break
            
            if not downloaded_file:
                # Fallback: get the most recent file
                files = [f for f in os.listdir('downloads') if f != '.gitkeep']
                if files:
                    downloaded_file = max(files, key=lambda f: os.path.getctime(os.path.join('downloads', f)))
            
            if downloaded_file:
                # Update download record
                file_path = os.path.join('downloads', downloaded_file)
                file_size = os.path.getsize(file_path)
                download_record.file_size = file_size
                download_record.status = 'completed'
                download_record.completed_at = datetime.utcnow()
                db.session.commit()
                
                # Log analytics
                analytics = Analytics(
                    event_type='download_completed',
                    platform=platform,
                    url=url,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    event_metadata=json.dumps({
                        'title': title,
                        'download_type': 'audio' if audio_only else 'video',
                        'file_size': file_size
                    })
                )
                db.session.add(analytics)
                db.session.commit()
                
                return send_file(file_path, as_attachment=True, download_name=downloaded_file)
            else:
                download_record.status = 'failed'
                db.session.commit()
                return jsonify({'error': 'Download completed but file not found'}), 500
                
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        
        # Update download record
        if download_record:
            download_record.status = 'failed'
            db.session.commit()
        
        # Log error
        try:
            error_log = ErrorLog(
                error_type='download_error',
                error_message=str(e),
                url=url,
                platform=platform,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                stack_trace=str(e)
            )
            db.session.add(error_log)
            db.session.commit()
        except Exception as log_error:
            logging.error(f"Error logging failed: {str(log_error)}")
        
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/get_info')
def get_info():
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    platform = detect_platform(url)
    
    # Handle example URLs
    if 'example' in url.lower() or url.endswith('/example'):
        return jsonify({
            'title': f'Example {platform.title()} Video',
            'duration': 180,
            'thumbnail': '/static/og-image.svg',
            'uploader': f'Example {platform.title()} Channel',
            'view_count': 1000000,
            'description': f'This is an example {platform} video. Replace with a real URL to get actual video information.'
        })
    
    try:
        # Log info request
        analytics = Analytics(
            event_type='info_request',
            platform=platform,
            url=url,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(analytics)
        db.session.commit()
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
            })
            
    except Exception as e:
        logging.error(f"Info extraction error: {str(e)}")
        
        # Log error
        try:
            error_log = ErrorLog(
                error_type='info_extraction_error',
                error_message=str(e),
                url=url,
                platform=platform,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                stack_trace=str(e)
            )
            db.session.add(error_log)
            db.session.commit()
        except Exception as log_error:
            logging.error(f"Error logging failed: {str(log_error)}")
        
        return jsonify({'error': f'Failed to extract info: {str(e)}'}), 500

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if email already exists
        existing = Newsletter.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                return jsonify({'error': 'Email already subscribed'}), 400
            else:
                # Reactivate subscription
                existing.is_active = True
                existing.subscribed_at = datetime.utcnow()
                db.session.commit()
                return jsonify({'message': 'Successfully resubscribed to newsletter!'})
        
        # Create new subscription
        newsletter = Newsletter(
            email=email,
            ip_address=request.remote_addr
        )
        db.session.add(newsletter)
        db.session.commit()
        
        # Log analytics
        analytics = Analytics(
            event_type='newsletter_subscription',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            event_metadata=json.dumps({'email': email})
        )
        db.session.add(analytics)
        db.session.commit()
        
        return jsonify({'message': 'Successfully subscribed to newsletter!'})
        
    except Exception as e:
        logging.error(f"Newsletter subscription error: {str(e)}")
        return jsonify({'error': 'Subscription failed. Please try again.'}), 500

@app.route('/admin/downloads')
def admin_downloads():
    """Admin endpoint to view download statistics"""
    try:
        downloads = Download.query.order_by(Download.created_at.desc()).limit(100).all()
        return jsonify([download.to_dict() for download in downloads])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/analytics')
def admin_analytics():
    """Admin endpoint to view analytics"""
    try:
        analytics = Analytics.query.order_by(Analytics.created_at.desc()).limit(100).all()
        return jsonify([analytic.to_dict() for analytic in analytics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard page"""
    return render_template('admin.html')

@app.route('/admin/newsletter')
def admin_newsletter():
    """Admin endpoint to view newsletter subscriptions"""
    try:
        newsletters = Newsletter.query.order_by(Newsletter.subscribed_at.desc()).all()
        return jsonify([newsletter.to_dict() for newsletter in newsletters])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO"""
    from datetime import datetime
    return render_template('sitemap.xml', current_date=datetime.now().strftime('%Y-%m-%d')), 200, {'Content-Type': 'application/xml'}

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    return render_template('robots.txt'), 200, {'Content-Type': 'text/plain'}

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

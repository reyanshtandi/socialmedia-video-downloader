# SnapSaver - Social Media Downloader

## Overview

SnapSaver is a Flask-based web application that allows users to download videos and media from various social media platforms including YouTube, Instagram, TikTok, Twitter, and Facebook. The application features a clean, responsive interface with platform detection and uses yt-dlp for media downloading.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Media Downloader**: yt-dlp library for extracting media from social platforms
- **File Management**: Custom cleanup system for temporary file management
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python logging module for debugging and monitoring
- **Analytics**: Database-driven analytics and error tracking

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome for platform icons and UI elements
- **JavaScript**: Vanilla JavaScript with custom classes for theme management and notifications
- **Styling**: Custom CSS with dark/light theme support
- **Templates**: Jinja2 templating with base template inheritance

## Key Components

### Platform Detection System
- **File**: `platform_detector.py`
- **Purpose**: Identifies social media platforms from URLs
- **Supported Platforms**: YouTube, Instagram, TikTok, Twitter/X, Facebook
- **Method**: URL parsing with domain matching and normalization

### Database Models
- **Files**: `models.py`
- **Models**:
  - Download: Tracks download history with metadata
  - Newsletter: Manages email subscriptions
  - Analytics: Logs user interactions and events
  - ErrorLog: Stores error information for debugging
- **Features**:
  - Complete download tracking from request to completion
  - Analytics for usage patterns and platform popularity
  - Newsletter subscription management
  - Error logging and monitoring

### File Management System
- **Files**: `cleanup.py`, `file_manager.py`
- **Purpose**: Manages temporary downloaded files
- **Features**: 
  - Automatic cleanup of files older than 15 minutes
  - Background thread for periodic cleanup (every 5 minutes)
  - Manual cleanup functionality

### Template System
- **Base Template**: `templates/base.html` with navigation and common elements
- **Platform Pages**: Dedicated templates for each social media platform
- **Features**: 
  - Responsive design
  - Theme toggle (dark/light)
  - Flash message system
  - Platform-specific styling

### Static Assets
- **CSS**: Custom styling with CSS variables for theming
- **JavaScript**: Theme management and UI interactions
- **External Dependencies**: Bootstrap, Font Awesome via CDN

## Data Flow

1. **URL Input**: User enters social media URL on homepage
2. **Platform Detection**: `detect_platform()` function identifies the platform
3. **Database Logging**: Analytics entry created for platform detection
4. **Routing**: User redirected to platform-specific page
5. **Info Extraction**: yt-dlp extracts media metadata for preview
6. **Download Request**: User initiates download, record created in database
7. **Media Processing**: yt-dlp downloads content, database updated with progress
8. **File Serving**: Flask serves downloaded file to user
9. **Completion**: Download record marked as completed with file size and metadata
10. **Cleanup**: Background thread removes old files automatically
11. **Analytics**: All interactions logged for monitoring and statistics

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **yt-dlp**: Media downloader (successor to youtube-dl)
- **Standard Library**: os, logging, threading, time, urllib.parse, json

### Frontend Dependencies (CDN)
- **Bootstrap 5.3.0**: CSS framework
- **Font Awesome 6.4.0**: Icon library

### Platform APIs
- Indirect access through yt-dlp to various social media platforms
- No direct API integration required

## Deployment Strategy

### File Structure
```
/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── platform_detector.py  # URL platform detection
├── cleanup.py            # File cleanup utilities
├── file_manager.py       # File management class
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── [platform].html
├── static/               # Static assets
│   ├── style.css
│   └── script.js
└── downloads/            # Temporary file storage
```

### Environment Configuration
- **Session Secret**: Configurable via `SESSION_SECRET` environment variable
- **Debug Mode**: Enabled in development
- **Host/Port**: Configured for 0.0.0.0:5000 in main.py

### File Management
- **Downloads Directory**: Created automatically if not exists
- **Cleanup Strategy**: Automatic deletion of files older than 15 minutes
- **Background Processing**: Daemon thread for continuous cleanup

### Security Considerations
- Session secret should be set in production
- File cleanup prevents disk space issues
- URL validation prevents malicious input
- Flash messages for user feedback

## Recent Changes

### January 2025 - SEO Optimization
- Added comprehensive SEO meta tags (title, description, keywords)
- Implemented Open Graph and Twitter Card metadata
- Added structured data (JSON-LD) for better search engine understanding
- Created sitemap.xml and robots.txt for search engine crawling
- Enhanced homepage content with SEO-friendly features section
- Added "How it Works" section with keyword-rich content
- Improved platform-specific page titles and descriptions
- Created social media sharing image (og-image.svg)

### Database Integration
- Added PostgreSQL database with comprehensive tracking
- Created models for downloads, newsletters, analytics, and error logs
- All user interactions are now tracked and stored
- Admin dashboard available at /admin for monitoring
- Newsletter subscription system with email validation

### Platform-Specific Pages Enhancement
- Created dedicated pages for YouTube, Instagram, TikTok, Twitter, and Facebook
- Enhanced each platform page with specific features and benefits
- Added platform-specific SEO meta tags and descriptions
- Improved download options with video/audio format selection
- Added informative features sections for each platform
- Enhanced user experience with platform-specific styling and icons

### Additional Features Added
- Fixed example URL handling to prevent console errors
- Added ffmpeg support for audio extraction and video processing
- Created comprehensive admin dashboard with statistics and data tables
- Added Terms of Service and Privacy Policy pages
- Enhanced error handling and user feedback
- Improved database tracking and analytics
- Added proper file management and cleanup system

## Notes

- The application is designed to be lightweight and self-contained
- Database-driven tracking and analytics for all user interactions
- Platform-specific pages are prepared but download functionality may need completion
- Theme system supports both light and dark modes with localStorage persistence
- Error handling includes user-friendly flash messages and logging
- SEO-optimized with proper meta tags, structured data, and content optimization
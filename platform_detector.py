from urllib.parse import urlparse
import re

def detect_platform(url):
    """
    Detect the social media platform from a URL
    Returns: 'youtube', 'instagram', 'tiktok', 'twitter', 'facebook', or 'unknown'
    """
    if not url:
        return 'unknown'
    
    # Normalize URL
    url = url.strip().lower()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Platform detection
        if domain in ['youtube.com', 'youtu.be', 'm.youtube.com']:
            return 'youtube'
        elif domain in ['instagram.com', 'm.instagram.com']:
            return 'instagram'
        elif domain in ['tiktok.com', 'm.tiktok.com', 'vm.tiktok.com']:
            return 'tiktok'
        elif domain in ['twitter.com', 'x.com', 'm.twitter.com', 'mobile.twitter.com']:
            return 'twitter'
        elif domain in ['facebook.com', 'm.facebook.com', 'web.facebook.com']:
            return 'facebook'
        else:
            return 'unknown'
            
    except Exception:
        return 'unknown'

def validate_url(url):
    """
    Validate if the URL is properly formatted
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and parsed.netloc
    except:
        return False

def extract_video_id(url, platform):
    """
    Extract video ID from URL for different platforms
    """
    if platform == 'youtube':
        # YouTube video ID extraction
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
    
    elif platform == 'instagram':
        # Instagram post ID extraction
        match = re.search(r'(?:p|reel)\/([A-Za-z0-9_-]+)', url)
        if match:
            return match.group(1)
    
    elif platform == 'tiktok':
        # TikTok video ID extraction
        match = re.search(r'video\/(\d+)', url)
        if match:
            return match.group(1)
    
    return None

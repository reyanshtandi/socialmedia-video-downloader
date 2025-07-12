from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float

def create_models(db):
    class Download(db.Model):
        """Model for tracking download history"""
        __tablename__ = 'downloads'
        
        id = Column(Integer, primary_key=True)
        url = Column(String(500), nullable=False)
        platform = Column(String(50), nullable=False)
        title = Column(String(200), nullable=True)
        uploader = Column(String(100), nullable=True)
        duration = Column(Float, nullable=True)
        view_count = Column(Integer, nullable=True)
        file_size = Column(Integer, nullable=True)
        download_type = Column(String(20), default='video')  # video, audio
        status = Column(String(20), default='pending')  # pending, completed, failed
        ip_address = Column(String(45), nullable=True)
        user_agent = Column(String(500), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)
        
        def __repr__(self):
            return f'<Download {self.id}: {self.platform} - {self.title}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'url': self.url,
                'platform': self.platform,
                'title': self.title,
                'uploader': self.uploader,
                'duration': self.duration,
                'view_count': self.view_count,
                'file_size': self.file_size,
                'download_type': self.download_type,
                'status': self.status,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            }

    class Newsletter(db.Model):
        """Model for newsletter subscriptions"""
        __tablename__ = 'newsletter'
        
        id = Column(Integer, primary_key=True)
        email = Column(String(120), unique=True, nullable=False)
        is_active = Column(Boolean, default=True)
        subscribed_at = Column(DateTime, default=datetime.utcnow)
        ip_address = Column(String(45), nullable=True)
        
        def __repr__(self):
            return f'<Newsletter {self.email}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'is_active': self.is_active,
                'subscribed_at': self.subscribed_at.isoformat() if self.subscribed_at else None
            }

    class Analytics(db.Model):
        """Model for storing analytics data"""
        __tablename__ = 'analytics'
        
        id = Column(Integer, primary_key=True)
        event_type = Column(String(50), nullable=False)
        platform = Column(String(50), nullable=True)
        url = Column(String(500), nullable=True)
        ip_address = Column(String(45), nullable=True)
        user_agent = Column(String(500), nullable=True)
        event_metadata = Column(Text, nullable=True)  # JSON string for additional data
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Analytics {self.event_type}: {self.platform}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'event_type': self.event_type,
                'platform': self.platform,
                'url': self.url,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class ErrorLog(db.Model):
        """Model for storing error logs"""
        __tablename__ = 'error_logs'
        
        id = Column(Integer, primary_key=True)
        error_type = Column(String(50), nullable=False)
        error_message = Column(Text, nullable=False)
        url = Column(String(500), nullable=True)
        platform = Column(String(50), nullable=True)
        ip_address = Column(String(45), nullable=True)
        user_agent = Column(String(500), nullable=True)
        stack_trace = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<ErrorLog {self.error_type}: {self.error_message[:50]}>'
        
        def to_dict(self):
            return {
                'id': self.id,
                'error_type': self.error_type,
                'error_message': self.error_message,
                'url': self.url,
                'platform': self.platform,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return Download, Newsletter, Analytics, ErrorLog
import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    
    if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_safe_avatar_url(url: str) -> bool:
    if not url:
        return True
    

    if url == "default.svg":
        return True
    
    allowed_schemes = {'http', 'https'}
    
    try:
        result = urlparse(url)

        if not result.scheme:
            return True
        if result.scheme not in allowed_schemes:
            return False
        
        dangerous_patterns = ['javascript', 'data:', 'vbscript', '<script']
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in dangerous_patterns):
            return False
        
        return True
    except Exception:
        return False


def sanitize_username(username: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '', username)

"""
Input validation and sanitization utilities.

Provides functions to sanitize user input and prevent XSS attacks.
"""

import bleach
from typing import Optional


# Allowed HTML tags and attributes for sanitized content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class']
}


def sanitize_html(text: Optional[str]) -> Optional[str]:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Removes dangerous HTML tags and attributes while preserving
    basic formatting tags.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Sanitized text with only allowed HTML tags, or None if input is None
    """
    if text is None:
        return None
    
    # Strip all HTML tags and convert to plain text
    # For HR portal, we don't allow any HTML in user input
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def sanitize_text(text: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """
    Sanitize plain text input.
    
    Removes HTML tags and optionally enforces maximum length.
    
    Args:
        text: Input text
        max_length: Optional maximum length to enforce
        
    Returns:
        Sanitized text or None if input is None
    """
    if text is None:
        return None
    
    # Remove any HTML tags
    sanitized = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Trim to max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Strip leading/trailing whitespace
    return sanitized.strip()


def validate_reference_format(reference: str) -> bool:
    """
    Validate that a reference follows the expected format: REF-YYYY-NNN.
    
    Args:
        reference: Reference string to validate
        
    Returns:
        True if reference is valid, False otherwise
    """
    import re
    pattern = r'^REF-\d{4}-\d{3}$'
    return bool(re.match(pattern, reference))


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email appears valid, False otherwise
    """
    import re
    # Basic email pattern - not exhaustive but catches obvious issues
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

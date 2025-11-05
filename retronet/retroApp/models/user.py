"""
User model functions for retroNet
Handles all user-related database operations
"""

from werkzeug.security import generate_password_hash, check_password_hash
from retroApp.models.db import get_db
from datetime import datetime


def get_user_by_id(user_id):
    """Get user by ID"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    return user


def get_user_by_username(username):
    """Get user by username"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    return user


def create_user(username, password, key):
    """Create a new user
    
    Args:
        username: Unique username
        password: Plain text password (will be hashed)
    
    Returns:
        user_id if successful, None if username exists
    """
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO user (username, password, key) VALUES (?, ?)",
            (username, generate_password_hash(password), key),
        )
        db.commit()
        return cursor.lastrowid
    except db.IntegrityError:
        # Username already exists
        return None


def authenticate_user(username, password):
    """Authenticate user credentials
    
    Args:
        username: Username to check
        password: Plain text password to verify
    
    Returns:
        User dict if valid, None if invalid
    """
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None


def update_last_seen(user_id):
    """Update user's last_seen timestamp"""
    db = get_db()
    try:
        db.execute(
            "UPDATE user SET last_seen = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        db.commit()
    except Exception as e:
        print(f"Error updating last_seen: {e}")


def get_user_profile(username):
    """Get user profile data including stats
    
    Args:
        username: Username to get profile for
    
    Returns:
        Dict with user info and stats, or None if not found
    """
    db = get_db()
    user = get_user_by_username(username)
    
    if not user:
        return None
    
    # Get user's blog post count
    post_count = db.execute(
        'SELECT COUNT(*) as count FROM user_blog_post WHERE author_id = ?',
        (user['id'],)
    ).fetchone()['count']
    
    # Get user's recent posts
    recent_posts = db.execute(
        '''SELECT id, title, body, created 
           FROM user_blog_post 
           WHERE author_id = ? 
           ORDER BY created DESC 
           LIMIT 5''',
        (user['id'],)
    ).fetchall()
    
    # TODO: Get stalker count when implemented
    stalker_count = 0
    
    return {
        'user': user,
        'post_count': post_count,
        'recent_posts': recent_posts,
        'stalker_count': stalker_count,
        'profile_music': user['profile_music'],
        'profile_customized': user['profile_customized']
    }


def update_profile_music(user_id, music_url):
    """Update user's profile music
    
    Args:
        user_id: User ID
        music_url: URL to music file or embed code
    """
    db = get_db()
    try:
        db.execute(
            "UPDATE user SET profile_music = ? WHERE id = ?",
            (music_url, user_id)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating profile music: {e}")
        return False


def mark_profile_customized(user_id):
    """Mark user's profile as customized
    
    Args:
        user_id: User ID
    """
    db = get_db()
    try:
        db.execute(
            "UPDATE user SET profile_customized = 1 WHERE id = ?",
            (user_id,)
        )
        db.commit()
    except Exception as e:
        print(f"Error marking profile customized: {e}")


def get_all_users(limit=10):
    """Get list of all users (for discovery)
    
    Args:
        limit: Maximum number of users to return
    
    Returns:
        List of user dicts
    """
    db = get_db()
    users = db.execute(
        '''SELECT id, username, last_seen, profile_customized 
           FROM user 
           ORDER BY last_seen DESC 
           LIMIT ?''',
        (limit,)
    ).fetchall()
    return users


def search_users(query):
    """Search for users by username
    
    Args:
        query: Search query
    
    Returns:
        List of matching users
    """
    db = get_db()
    users = db.execute(
        '''SELECT id, username, last_seen, profile_customized 
           FROM user 
           WHERE username LIKE ? 
           ORDER BY username 
           LIMIT 20''',
        (f'%{query}%',)
    ).fetchall()
    return users
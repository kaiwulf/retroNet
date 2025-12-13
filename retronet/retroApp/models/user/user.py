"""
User model functions for retroNet
Handles all user-related database operations
"""

from werkzeug.security import generate_password_hash, check_password_hash
from retroApp.models.db import get_db
from datetime import datetime

def get_username_by_id(user_id):
    db = get_db()
    username = db.execute(
        'SELECT username FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    return username

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
    """Get all data used on user profile
    
    Args:
        username: Username to get profile for
    
    Returns:
        Dict with user info and stats, or None if not found
    """
    db = get_db()
    user_row = get_user_by_username(username)
    
    if not user_row:
        return None
    
    user = dict(user_row)

    # Get user's blog post count
    post_count = db.execute(
        'SELECT COUNT(*) as count FROM user_blog_post WHERE author_id = ?',
        (user['id'],)
    ).fetchone()['count']
    
    # Get user's recent posts
    recent_posts = db.execute(
        '''SELECT id, title, body, created_at 
           FROM user_blog_post 
           WHERE author_id = ? 
           ORDER BY created_at DESC 
           LIMIT 5''',
        (user['id'],)
    ).fetchall()

    recent_posts = [dict(post) for post in recent_posts]
    
    if len(recent_posts) == 0:
        recent_posts = [
            {
                'id': 1,
                'title': 'Welcome to My Profile!',
                'body': 'Just joined retroNet. Excited to be part of this community!',
                'created_at': datetime(2024, 11, 5, 10, 30)
            },
            {
                'id': 2,
                'title': 'Learning Flask',
                'body': 'Been diving into Flask development. It\'s pretty cool!',
                'created_at': datetime(2024, 11, 12, 14, 15)
            },
            {
                'id': 3,
                'title': 'Retro Web Design',
                'body': 'Love the aesthetic of early 2000s web design. Bringing it back!',
                'created_at': datetime(2024, 11, 20, 9, 45)
            }
        ]
        post_count = 3

    music = get_users_music_list(user['id'])
    if music is None:
        music = {}
        music['track_name'] = 'Never Gonna Give You Up'  # ← Not empty
        music['artist_name'] = 'Rick Astley'
        music['album_name'] = 'Whenever You Need Somebody'

    # Get stalkers by user's id
    stalker_list = get_stalkers(user['id'])
    stalker_profiles = [get_stalker_profile(profile['id']) for profile in stalker_list]

    stalker_profiles = [dict(profile) for profile in stalker_profiles if profile]

    # Add dummy stalkers if none exist
    if len(stalker_list) == 0:
        stalker_list = [
            {
                'id': 101,
                'username': 'alice123',
                'display_name': 'Alice',
                'bio': 'Love retroNet! Old web vibes forever.',
                'stalker_count': 15,
                'stalking_since': datetime(2024, 11, 15, 12, 30)
            },
            {
                'id': 102,
                'username': 'bob_rocks',
                'display_name': 'Bob',
                'bio': 'Tech enthusiast and blogger',
                'stalker_count': 8,
                'stalking_since': datetime(2024, 11, 20, 16, 45)
            },
            {
                'id': 103,
                'username': 'charlie99',
                'display_name': 'Charlie',
                'bio': 'Just here for the vibes',
                'stalker_count': 23,
                'stalking_since': datetime(2024, 12, 1, 9, 15)
            },
            {
                'id': 104,
                'username': 'dana_codes',
                'display_name': 'Dana',
                'bio': 'Full-stack dev learning Flask',
                'stalker_count': 12,
                'stalking_since': datetime(2024, 12, 5, 14, 20)
            },
            {
                'id': 105,
                'username': 'retro_fan',
                'display_name': 'RetroFan',
                'bio': '90s web aesthetic enthusiast',
                'stalker_count': 31,
                'stalking_since': datetime(2024, 12, 8, 11, 00)
            }
        ]
        stalker_profiles = stalker_list
        stalker_count = 5
    else:
        stalker_count = len(stalker_list)

    feed_items = [
        {
            'type': 'forum',
            'source': 'Tech Discussion',
            'title': 'Help with Python',
            'url': '/forum/posts/123',
            'timestamp': datetime(2024, 12, 12)
        },
        {
            'type': 'usenet',
            'source': 'comp.lang.python',
            'subject': 'Re: Best practices',
            'url': '/usenet/messages/456',
            'timestamp': datetime(2024, 12, 11)
        }
    ]

    comments = [
        {
            'body': 'Great profile! Love the music choice.',
            'timestamp': datetime(2024, 12, 12, 14, 30),
            'author': {
                'username': 'alice123',
                'url': '/profile/alice123'
            }
        },
        {
            'body': 'Thanks for the add!',
            'timestamp': datetime(2024, 12, 11, 10, 15),
            'author': {
                'username': 'bob_rocks',
                'url': '/profile/bob_rocks'
            }
        },
        {
            'body': 'Check out my new blog post',
            'timestamp': datetime(2024, 12, 10, 18, 45),
            'author': {
                'username': 'charlie99',
                'url': '/profile/charlie99'
            }
        }
    ]

    comment_count = len(comments)

    # print(f"in user model... user data is...\n{user}")

    user['post_count'] = post_count
    user['recent_blog_posts'] = recent_posts
    user['track_name'] = music['track_name']
    user['artist_name'] = music['artist_name']
    user['album_name'] = music['album_name']
    user['feed_items'] = feed_items
    user['comments'] = comments
    user['comment_count'] = comment_count
    user['profile_song'] = "assets/song.mp3"
    user['website'] = "kaiwulf.dev"
    user['location'] = "Texas"
    user['age'] = 22
    user['created_at'] = datetime(2024, 12, 10, 18, 45)
    user['stalker_count'] = stalker_count
    user['stalker_list'] = stalker_list
    user['stalker_profiles'] = stalker_profiles
    user['bg_color'] = '#ffffff'
    user['bg_image'] = None
    user['text_color'] = '#000000'

    return user
    # {
    #     'user': user,
    #     'post_count': post_count,
    #     'recent_blog_posts': recent_posts,
    #     'stalker_count': user['stalker_count'],
    #     'stalker_list': user['stalker_list'],
    #     'track_name': music['track_name'],
    #     'artist_name': music['artist_name'],
    #     'album_name': music['album_name'],
    #     'feed_items': feed_items,
    #     'comments': comments,
    #     'comment_count': comment_count
    # }

# def get_users_usenet_feed(user_id):
#     """Retrieve users usenet feed

#     Args:
#         user_id: User ID
#     """
#     db = get_db()
#     try:
#         usenet_feed = db.execute(
#             "SELECT "
#         )

def get_users_music_list(user_id):
    """Retrieve users profile music

    Args:
        user_id: User ID
    """
    db = get_db()
    try:
        user_music = db.execute(
            "SELECT track_name, artist_name, album_name FROM user_music WHERE user_id = ?", (user_id,)
        ).fetchone()
        print(f"fetching user_music {user_music}")
    except Exception as e:
        print("Error fetching user music list '{e}'")
    return user_music

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

def get_stalkers(user_id):
    """
    Get all users who are stalking this user (their followers).
    
    Args:
        user_id: The stalked user's ID
        db_path: Path to database
        
    Returns:
        List of dicts containing user info of their stalkers
    """
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            user.id,
            user.username,
            user.display_name,
            user.bio,
            user.stalker_count,
            stalker.created_at as stalking_since
        FROM stalker
        JOIN user ON stalker.stalker_id = user.id
        WHERE stalker.stalked_id = ?
        ORDER BY stalker.created_at DESC
    """, (user_id,))
    
    results = cursor.fetchall()
    db.close()
    
    return [dict(row) for row in results]

def get_stalker_profile(stalker_id):
    db = get_db()
    stalker_profile = get_user_by_id(stalker_id)
    return stalker_profile

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
from flask import Blueprint, jsonify, render_template
import json
import time
from retroApp.models.db import get_db

bp = Blueprint('landing', __name__)

@bp.route('/')
def landing():
    """Main landing page for retroNet"""
    return render_template('landing/landing.html')

# ═══════════════════════════════════════════════════════════
# Live Stats with AJAX Polling
# ═══════════════════════════════════════════════════════════

@bp.route('/api/stats')
def get_stats():
    """API endpoint for live stats - AJAX polling version"""
    try:
        db = get_db()
        
        stats = {
            'visitors': get_visitor_count(db),
            'members': get_total_members(db),
            'active_now': get_active_users(db),
            'profiles_pimped': get_profiles_count(db),
            'songs_playing': get_active_songs(db),
            'glitter_used': '∞'
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({
            'error': True,
            'visitors': 1337,
            'members': 0,
            'active_now': 0,
            'profiles_pimped': 0,
            'songs_playing': 0
        }), 500

# Helper functions (same as before)
def get_visitor_count(db):
    try:
        result = db.execute('SELECT COUNT(*) as count FROM visitors').fetchone()
        return result['count'] if result else 0
    except:
        return 1337

def get_total_members(db):
    try:
        result = db.execute('SELECT COUNT(*) as count FROM user').fetchone()
        return result['count'] if result else 0
    except:
        return 0

def get_active_users(db):
    try:
        result = db.execute('''
            SELECT COUNT(*) as count FROM user 
            WHERE last_seen > datetime('now', '-15 minutes')
        ''').fetchone()
        return result['count'] if result else 0
    except:
        return 0

def get_profiles_count(db):
    try:
        result = db.execute('''
            SELECT COUNT(*) as count FROM user 
            WHERE profile_customized = 1
        ''').fetchone()
        return result['count'] if result else 0
    except:
        return 0

def get_active_songs(db):
    try:
        result = db.execute('''
            SELECT COUNT(*) as count FROM user 
            WHERE profile_music IS NOT NULL AND profile_music != ''
        ''').fetchone()
        return result['count'] if result else 0
    except:
        return 0
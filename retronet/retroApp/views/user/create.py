from flask import (
    Blueprint, g, render_template, request, flash, redirect, url_for
)
from retroApp.models.user.user import get_user_profile
from retroApp.models.user.create import create_profile

bp = Blueprint('create', __name__, url_prefix='/create')

@bp.route('/<username>', methods=('GET', 'POST'))
def new_profile(username):
    print(f"new_profile username {username}")
    try:
        if request.method == 'POST':
            print("creating profile")
            display_name = request.form['display']
            print(f"display: {display_name}")
            track_name = request.form['track']
            print(f"track: {track_name}")
            artist_name = request.form['artist']
            print(f"artist: {artist_name}")
            album_name = request.form['album']
            print(f"album: {album_name}")
            bio = request.form['bio']
            print(f"bio: {bio}")
            if create_profile(display_name, bio, track_name, artist_name, album_name, username):
                flash("Profile created successfully!")
                return redirect(url_for('user.profile', username=username))
            else:
                flash("Error creating profile :(")
    except Exception as e:
        print(f"Error creating profile: \"{e}\"")
    return render_template('user/create/create.html', username=username)
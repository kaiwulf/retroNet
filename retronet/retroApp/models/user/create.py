from retroApp.models.db import get_db
from flask import flash
def create_profile(display_name, bio, track_name, artist_name, album_name, username):
    db = get_db()
    try:
        db.execute(
            "UPDATE user SET display_name = ?, bio = ? WHERE username = ?",
            (display_name, bio, username)
        )

        user = db.execute(
            "SELECT id FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            raise Exception(f"User {username} not found")
        
        user_id = user['id']
    except db.IntegrityError as e:
        error = f"Failure to save {display_name} and bio:\n"
        + "{Bio}"
        + "because of error '{e}'"
        db.rollback()
        return False
    try:
        db.execute(
            "INSERT INTO user_music (user_id, track_name, artist_name, album_name, spotify_track_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, track_name, artist_name, album_name, "1234567890"),
        )
        
        db.commit()
        return True
    except db.IntegrityError as e:
        error = f"Failure to save {track_name}, {artist_name}, and/or {album_name} due to error '{e}'"
        print(error)
        flash(error)
        db.rollback()
        return False
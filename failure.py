# retronet/retroApp/views/auth/auth.py
@bp.route('/signin', methods=('GET','POST'))
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            print(f"Going to user.profile")
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('user.profile'), username=username)
        flash(error, 'error')
    return render_template('auth/signin.html')

# retronet/retroApp/views/user.py
bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/<username>')
def profile(username):
    """User profile page
    
    Shows user's profile including:
    - Profile info
    - Blog posts
    - Stalker count
    - Profile music
    """
    # Get user profile data from model
    print(f"In user profile")
    profile_data = get_user_profile(username)
    print(f"profile data is: {profile_data}")
    
    if profile_data is None:
        abort(404, f"User '{username}' not found")
    
    # Check if viewing own profile
    is_own_profile = False
    if g.user and g.user['username'] == username:
        is_own_profile = True
    
    return render_template(
        'user/profile.html',
        profile=profile_data,
        is_own_profile=is_own_profile
    )

#     --------
# error when logging in:

# Traceback (most recent call last):
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 1511, in wsgi_app
#     response = self.full_dispatch_request()
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 919, in full_dispatch_request
#     rv = self.handle_user_exception(e)
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 917, in full_dispatch_request
#     rv = self.dispatch_request()
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 902, in dispatch_request
#     return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
#            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
#   File "/home/kai/dev/retroNet/retronet/retroApp/views/auth/auth.py", line 62, in signin
#     return redirect(url_for('user.profile'), username=username)
#                     ~~~~~~~^^^^^^^^^^^^^^^^
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/helpers.py", line 239, in url_for
#     return current_app.url_for(
#            ~~~~~~~~~~~~~~~~~~~^
#         endpoint,
#         ^^^^^^^^^
#     ...<4 lines>...
#         **values,
#         ^^^^^^^^^
#     )
#     ^
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 1121, in url_for
#     return self.handle_url_build_error(error, endpoint, values)
#            ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/flask/app.py", line 1110, in url_for
#     rv = url_adapter.build(  # type: ignore[union-attr]
#         endpoint,
#     ...<3 lines>...
#         force_external=_external,
#     )
#   File "/home/kai/dev/retroNet/lib/python3.13/site-packages/werkzeug/routing/map.py", line 924, in build
#     raise BuildError(endpoint, values, method, self)
# werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'user.profile'. Did you forget to specify values ['username']?

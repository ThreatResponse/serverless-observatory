import api
import analyze
import grade
import auth
import config
import json
import logging
import os
import user

from flask import (
    Flask, render_template, jsonify, redirect, session, request, url_for
)

from flask_assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

js = Bundle('js/base.js', filters='jsmin', output='js/gen/packed.js')
assets.register('js_all', js)

sass = Bundle('css/base.scss', filters='scss')
css = Bundle(sass, filters='cssmin', output='css/gen/all.css')
assets.register('css_all', css)

if os.environ.get('environment') is not 'Production':
    app.config.from_object(config.DevelopmentConfig())
else:
    app.config.from_object(config.ProductionConfig())

# Initializes Auth0 Support and loads decorator.
oidc_config = config.OIDCConfig()
authentication = auth.OpenIDConnect(oidc_config)
oidc = authentication.auth(app)

# Intializes the app logger.
handler = logging.StreamHandler()
logging.getLogger("werkzeug").addHandler(handler)


@app.route('/')
def index():
    return render_template(
        'home.html'
    )


@app.route('/dashboard')
@oidc.oidc_auth
def dashboard():
    u = user.User(session['userinfo'])
    return render_template(
        'dashboard.html',
        user=u
    )


@app.route('/settings')
@oidc.oidc_auth
def settings():
    u = user.User(session['userinfo'])
    return render_template(
        'settings.html',
        user=u
    )


@app.route('/info')
@oidc.oidc_auth
def info():
    """Return the JSONified user session for debugging."""
    return jsonify(
        id_token=session['id_token'],
        access_token=session['access_token'],
        userinfo=session['userinfo']
    )


@app.route('/logout')
@oidc.oidc_logout
def logout():

    """Route decorator destroys flask session and redirects to auth0 to destroy
    auth0 session.  Ending page is signout.html."""
    if os.environ.get('environment') == 'production':
        proto = "https"
    else:
        proto = "http"

    return_url = "{proto}://{server_name}/signout.html".format(
        proto=proto, server_name=app.config['SERVER_NAME']
    )

    return redirect(return_url, code=302)


@app.route('/signout.html')
def signout():
    return render_template('signout.html')


@app.route('/scan/<string:uuid>')
@oidc.oidc_auth
def get_scan(uuid):
    u = user.User(session['userinfo'])
    s = user.Scan(u).find_score_by_key(uuid)
    g = grade.Grade().get_grade(s)
    return render_template('report.html', user=u, score=s, grade=g)


@app.route('/scan/<string:uuid>/delete')
@oidc.oidc_auth
def delete_scan(uuid):
    u = user.User(session['userinfo'])
    p = api.Profiler(api_key=u.api_key)
    p.destroy_profile(uuid)
    # To-do destroy scores with this data.
    return redirect(url_for('dashboard'))


@app.route('/scan/<string:uuid>/score')
@oidc.oidc_auth
def score_scan(uuid):
    u = user.User(session['userinfo'])
    s = user.Scan(u).find_scan_by_key(uuid)
    a = analyze.ScoredTest(scan=s)
    a.run()
    return redirect(url_for('dashboard'))

# API Routes for serverless object storage
@app.route('/api/profile', methods=['POST'])
def profile_api():
    """Take a post to the profile, authenticate, and store appropriately."""
    if request.method == 'POST':
#       try:
        api_key = request.headers['authorization'].split(' ')[1]
        profiler = api.Profiler(api_key)
        profiler.store_profile(request.json)
        return json.dumps({'success': True}),
        200,
        {'ContentType': 'application/json'}
#        except:
#            return json.dumps({'success': False}),
#            500,
#            {'ContentType': 'application/json'}


@app.route('/api/key', methods=['POST'])
@oidc.oidc_auth
def api_key():
    if request.method == 'POST':
        try:
            u = user.User(session['userinfo'])
            u.rotate_api_key()
            return json.dumps({'success': True}),
            200,
            {'ContentType': 'application/json'}
        except:
            return json.dumps({'success': False}),
            500,
            {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run()

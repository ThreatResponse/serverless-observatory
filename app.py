import api
import analyze
import auth
import config
import grade
import json
import logging
import os
import observatory_configuration
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
    s = observatory_configuration.ScanConfig(u).find_configs_for_user()
    print(s)
    return render_template(
        'settings.html',
        user=u, configs=s
    )


@app.route('/configuration/new', methods=['GET', 'POST'])
@oidc.oidc_auth
def create_configuration():
    u = user.User(session['userinfo'])
    form = 'new'
    if request.method == 'POST':
        config = {
            'environment': request.form.get('environment', 'unknown'),
            'tennancy': request.form.get('tennancy', 'unknown'),
            'notes': request.form.get('notes', "No additional infomation.")
        }
        o = observatory_configuration.ScanConfig(user=u)
        o.create_configuration(configuration_information=config)
        return redirect('/settings')
    return render_template(
        'configuration.html',
        user=u, form=form
    )

@app.route('/configuration/<config_id>', methods=['GET', 'POST'])
@oidc.oidc_auth
def edit_configuration(config_id):
    u = user.User(session['userinfo'])
    o = observatory_configuration.ScanConfig(user=u).find_config_by_id(
        config_id=config_id
    )

    form = 'edit'

    if request.method == 'POST':
        config = {
            'uuid': o['uuid'],
            'user_id': u.user_id,
            'api_key': o['api_key'],
            'config': {
                'environment': request.form.get('environment', 'unknown'),
                'tennancy': request.form.get('tennancy', 'unknown'),
                'notes': request.form.get('notes', "No additional infomation.")
            },
            'disabled': o['disabled']
        }
        o = observatory_configuration.ScanConfig(user=u)
        o.update_configuration(config=config)
        return redirect('/settings')
    return render_template(
        'configuration.html',
        user=u, form=form, config=o['config'], config_id=config_id
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


@app.route('/scan/<string:profile_id>')
@oidc.oidc_auth
def get_scan(profile_id):
    u = user.User(session['userinfo'])
    s = user.Scan(u).find_score_by_key(profile_id)
    g = grade.Grade().get_grade(s)
    return render_template('report.html', user=u, score=s, grade=g)


@app.route('/scan/<string:profile_id>/delete')
@oidc.oidc_auth
def delete_scan(profile_id):
    p = api.Profiler()
    p.destroy_profile(profile_id)
    # To-do destroy scores with this data.
    return redirect(url_for('dashboard'))


@app.route('/scan/<string:profile_id>/score')
@oidc.oidc_auth
def score_scan(profile_id):
    u = user.User(session['userinfo'])
    s = user.Scan(u).find_scan_by_key(profile_id)
    a = analyze.ScoredTest(scan=s)
    a.run()
    return redirect(url_for('dashboard'))


# API Routes for serverless object storage
@app.route('/api/profile', methods=['POST'])
def profile_api():
    """Take a post to the profile, authenticate, and store appropriately."""
    if request.method == 'POST':
        #try:
        api_key = request.headers['authorization'].split(' ')[1]
        profiler = api.Profiler(api_key)
        print request.json
        profiler.store_profile(request.json)
        return json.dumps({'success': True}),
        200,
        {'ContentType': 'application/json'}
        #except:
        #    return json.dumps({'success': False}),
        #    500,
        #    {'ContentType': 'application/json'}


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

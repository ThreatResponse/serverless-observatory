import os
import config
import auth
import logging

from flask import (Flask, render_template, jsonify, redirect, session)

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
@oidc.oidc_auth
def home():
    return render_template(
        'home.html'
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


if __name__ == '__main__':
    app.run()

#!/usr/bin/python
"""Configuration loader for different environments."""

import credstash


class Config(object):
    """Defaults for the configuration objects."""
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = credstash.getSecret(
        name="observatory.secret_key",
        context={'app': 'serverless-observatory'},
        region="us-east-1"
    )
    SERVER_NAME = "serverless-observatory.threatresponse.cloud"
    SESSION_COOKIE_HTTPONLY = True
    LOGGER_NAME = "serverless-observatory"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class OIDCConfig(object):
    """Convienience Object for returning required vars to flask."""
    def __init__(self):
        """General object initializer."""
        self.OIDC_DOMAIN = credstash.getSecret(
            name="observatory.oidc_domain",
            context={'app': 'serverless-observatory'},
            region="us-east-1"
        )

        self.OIDC_CLIENT_ID = credstash.getSecret(
            name="observatory.client_id",
            context={'app': 'serverless-observatory'},
            region="us-east-1"
        )

        self.OIDC_CLIENT_SECRET = credstash.getSecret(
            name="observatory.client_secret",
            context={'app': 'serverless-observatory'},
            region="us-east-1"
        )

        self.LOGIN_URL = "https://{DOMAIN}/login?client={CLIENT_ID}".format(
            DOMAIN=self.OIDC_DOMAIN,
            CLIENT_ID=self.OIDC_CLIENT_ID
        )

    def auth_endpoint(self):
        return "https://{DOMAIN}/authorize".format(
            DOMAIN=self.OIDC_DOMAIN
        )

    def token_endpoint(self):
        return "https://{DOMAIN}/oauth/token".format(
            DOMAIN=self.OIDC_DOMAIN
        )

    def userinfo_endpoint(self):
        return "https://{DOMAIN}/userinfo".format(
            DOMAIN=self.OIDC_DOMAIN
        )

    def client_id(self):
        return self.OIDC_CLIENT_ID

    def client_secret(self):
        return self.OIDC_CLIENT_SECRET

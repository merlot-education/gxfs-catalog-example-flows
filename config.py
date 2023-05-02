import os

sd_wizard_api_base = "http://localhost:8085"
#catalog_api_base = "https://gxfscatalog.dev.merlot-education.eu"
catalog_api_base = "http://localhost:8081"
oauth_url = "https://sso.common.merlot-education.eu/realms/gxfscatalog/protocol/openid-connect/token"
oauth_client_secret = os.getenv('OAUTH2_CLIENT_SECRET')
oauth_user = "gxfscatalog"
oauth_pass = os.getenv('OAUTH2_PASS')


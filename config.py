import os

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081" # "https://gxfscatalog.dev.merlot-education.eu"
oauth_url = "http://key-server:8080/realms/gxfscatalog/protocol/openid-connect/token" # "https://sso.dev.merlot-education.eu/realms/gxfscatalog/protocol/openid-connect/token"
oauth_client_secret = "CScowEqRGIb6d7SLCZHVjKHIewp0ZmnO" #os.getenv('OAUTH2_CLIENT_SECRET')
oauth_user = "gxfscatalog"
oauth_pass = "gxfscatalog" #os.getenv('OAUTH2_PASS')


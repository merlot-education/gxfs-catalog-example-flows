"""
  Copyright 2023-2024 Dataport AöR
  
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""
import os

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081" # "https://gxfscatalog.dev.merlot-education.eu"
oauth_url = "http://key-server:8080/realms/gxfscatalog/protocol/openid-connect/token" # "https://sso.dev.merlot-education.eu/realms/gxfscatalog/protocol/openid-connect/token"
oauth_client_secret = "CScowEqRGIb6d7SLCZHVjKHIewp0ZmnO" #os.getenv('OAUTH2_CLIENT_SECRET')
oauth_user = "gxfscatalog"
oauth_pass = "gxfscatalog" #os.getenv('OAUTH2_PASS')


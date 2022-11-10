from typing import Callable, Optional
from fastapi import HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows, OAuthFlowClientCredentials
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
import os
import requests
import sys

AUTH_RESOURCE_NAME = os.environ.get('AUTH_RESOURCE_NAME','python-ex1')
AUTH_SERVER_URL_PRIVATE = os.environ.get('AUTH_SERVER_URL_PRIVATE', f'https://auth_server:8443/realms/{AUTH_RESOURCE_NAME}')
AUTH_SERVER_URL_PUBLIC = os.environ.get('AUTH_SERVER_URL_PUBLIC', f'https://127.0.0.1:8443/realms/{AUTH_RESOURCE_NAME}')
AUTH_SERVER_TOKEN_URL_PRIVATE = f'{AUTH_SERVER_URL_PRIVATE}/protocol/openid-connect/token'
AUTH_SERVER_TOKEN_URL_PUBLIC = f'{AUTH_SERVER_URL_PUBLIC}/protocol/openid-connect/token'

CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_auth_server_public_key():
    try:
        r = requests.get(AUTH_SERVER_URL_PRIVATE,
                        timeout=3, verify=False)
        r.raise_for_status()
        response_json = r.json()
        return f'-----BEGIN PUBLIC KEY-----\r\n{response_json["public_key"]}\r\n-----END PUBLIC KEY-----'
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("Unknow Error", err)
        sys.exit(1) 

AUTH_SERVER_PUBLIC_KEY = os.environ.get('AUTH_SERVER_PUBLIC_KEY', get_auth_server_public_key())

def decode_token(token: str):
    try:
        payload = jwt.decode(token, AUTH_SERVER_PUBLIC_KEY, algorithms=[ALGORITHMS.RS256],
                             options={"verify_signature": True, "verify_aud": False, "exp": True})
        # username: str | None = payload.get("preferred_username")
        return payload
    except JWTError as e:
        print(e)
        raise CREDENTIALS_EXCEPTION

def get_username(token: str) -> str | None:
    return decode_token(token=token).get("preferred_username")

def get_roles(token: str):
    decoded_token = decode_token(token=token)
    resource = decoded_token["resource_access"].get(AUTH_RESOURCE_NAME, None)
    resource_roles = resource["roles"] if resource else []
    realm_roles = decoded_token["realm_access"]["roles"]
    return resource_roles + realm_roles
    
def has_role(token: str, role: str):
    all_user_roles = get_roles(token=token)
    return (True if role in all_user_roles else False)

def __has_roles(token: str, roles: list[str], func: Callable):
    all_user_roles = get_roles(token=token)
    if func(elem in all_user_roles for elem in roles):
        return True
    else:
        return False

def has_all_roles(token: str, roles: list[str]):
    return __has_roles(token=token, roles=roles, func=all)
        
def has_any_role(token: str, roles: list[str]):
    return __has_roles(token=token, roles=roles, func=any)

# As Client Credentials was not merged to FastAPI yet, we must keep this class

class Oauth2ClientCredentials(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = "oAuth2ClientCredentials",
        scopes: dict | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(
            clientCredentials=OAuthFlowClientCredentials(tokenUrl=token_url, scopes=scopes)
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

from fastapi import FastAPI, Request, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBasicCredentials
from model import GoAroundMessage
import base64
import auth

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=auth.AUTH_SERVER_TOKEN_URL_PUBLIC)
oauth2_client_scheme = auth.Oauth2ClientCredentials(token_url=auth.AUTH_SERVER_TOKEN_URL_PUBLIC)

def common_output(token: str, message: GoAroundMessage | None = None):
    name = auth.get_username(token=token)
    result = {'name': name,
            'name_b64': base64.b64encode(name.encode('ascii')).decode('ascii') if name else None,
            'user_roles': auth.get_roles(token=token),
            'token': auth.decode_token(token=token)
        }
    if message: result["message"] = message.message
    return result

@app.get("/api/user/read_edp1",
        summary="This endpoint can be used by users admin1, user1 and user2. To understand why take a look on README.md"
    )
async def user_edp1(request: Request, token: str = Depends(oauth2_scheme)):
    if not auth.has_all_roles(token=token, roles=['common_user', 'read_data']):
        raise auth.CREDENTIALS_EXCEPTION
    return common_output(token=token)

@app.post("/api/user/write_edp1",
        summary="This endpoint can be used by users admin1 and user2. To understand why take a look on README.md"
    )
async def user_edp2(request: Request,  message: GoAroundMessage, token: str = Depends(oauth2_scheme)):
    if not auth.has_all_roles(token=token, roles=['common_user', 'write_data']):
        raise auth.CREDENTIALS_EXCEPTION
    return common_output(token=token, message=message)

@app.get("/api/admin/read_edp1",
        summary="This endpoint can be used by user admin1 only. To understand why take a look on README.md"
    )
async def admin_edp1(request: Request, token: str = Depends(oauth2_scheme)):
    if not auth.has_all_roles(token=token, roles=['admin_user', 'read_data']):
        raise auth.CREDENTIALS_EXCEPTION
    return common_output(token=token)

@app.post("/api/common/write_edp1",
        summary="This endpoint can be used by users admin1 and user2. To understand why take a look on README.md"
    )
async def common_write_edp1(request: Request,  message: GoAroundMessage, token: str = Depends(oauth2_scheme)):
    if not auth.has_any_role(token=token, roles=['admin_user', 'write_data']):
        raise auth.CREDENTIALS_EXCEPTION
    return common_output(token=token, message=message)

@app.get("/api/client/read_edp1",
        summary="This endpoint can be used only by authenticated client, not users. To understand why take a look on README.md"
    )
async def client_edp1(request: Request, token: str = Depends(oauth2_client_scheme)):
    if not auth.has_all_roles(token=token, roles=['client']):
        raise auth.CREDENTIALS_EXCEPTION
    return common_output(token=token)
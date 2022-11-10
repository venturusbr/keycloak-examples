from fastapi.testclient import TestClient
from main import app
from model import UserLogin, ClientCredentials, GoAroundMessage
import requests
import auth

test_client = TestClient(app)

headers = {}
headers["Content-Type"] = "application/x-www-form-urlencoded"

def get_access_token_password_flow(user_login: UserLogin, client_credentials: ClientCredentials, token_url: str):
    data = f'grant_type=password&username={user_login.username}&password={user_login.password}&'\
        f'client_id={client_credentials.client_id}&client_secret={client_credentials.client_secret}'
    token = requests.post(url=token_url, headers=headers, data=data, verify=False)
    return token.json()["access_token"]

def get_access_token_client_credentials_flow(client_credentials: ClientCredentials, token_url: str):
    data = f'grant_type=client_credentials&client_id={client_credentials.client_id}&client_secret={client_credentials.client_secret}'
    token = requests.post(url=token_url, headers=headers, data=data, verify=False)
    return token.json()["access_token"]

user1 = UserLogin(password='test1', username='user1')
user2 = UserLogin(password='test2', username='user2')
admin1 = UserLogin(password='testa', username='admin1')

ex1_client_credentials = ClientCredentials(client_id='python-ex1', client_secret='3RLY6WCCO4NWi54J7lFaQRjgBzfZlZ75')

user1_access_token = get_access_token_password_flow(user_login=user1, client_credentials=ex1_client_credentials, token_url=auth.AUTH_SERVER_TOKEN_URL_PRIVATE)
user2_access_token = get_access_token_password_flow(user_login=user2, client_credentials=ex1_client_credentials, token_url=auth.AUTH_SERVER_TOKEN_URL_PRIVATE)
admin1_access_token = get_access_token_password_flow(user_login=admin1, client_credentials=ex1_client_credentials, token_url=auth.AUTH_SERVER_TOKEN_URL_PRIVATE)
client_access_token = get_access_token_client_credentials_flow(client_credentials=ex1_client_credentials, token_url=auth.AUTH_SERVER_TOKEN_URL_PRIVATE)

_PERMISSION_MSG = GoAroundMessage(message="I have permission to write!").json()
_NO_PERMISSION_MSG = GoAroundMessage(message="I don't have permission to write!").json()

# User1
def test_user1_user_read_edp1():
    response = test_client.get(
        "/api/user/read_edp1",
        headers={"Authorization": f'Bearer {user1_access_token}'}
    )
    assert response.status_code == 200

def test_user1_user_write_edp1():
    response = test_client.post(
        "/api/user/write_edp1",
        headers={"Authorization": f'Bearer {user1_access_token}'},
        data=GoAroundMessage(message="I don't have permission to write!").json(),
    )
    assert response.status_code == 401

def test_user1_admin_read_edp1():
    response = test_client.get(
        "/api/admin/read_edp1",
        headers={"Authorization": f'Bearer {user1_access_token}'}
    )
    assert response.status_code == 401

def test_user1_common_write_edp1():
    response = test_client.post(
        "/api/common/write_edp1",
        headers={"Authorization": f'Bearer {user1_access_token}'},
        data=_NO_PERMISSION_MSG,
    )
    assert response.status_code == 401


def test_user1_client_read_edp1():
    response = test_client.get(
        "/api/client/read_edp1",
        headers={"Authorization": f'Bearer {user1_access_token}'},
    )
    assert response.status_code == 401

# User2
def test_user2_user_read_edp1():
    response = test_client.get(
        "/api/user/read_edp1",
        headers={"Authorization": f'Bearer {user2_access_token}'}
    )
    assert response.status_code == 200

def test_user2_user_write_edp1():
    response = test_client.post(
        "/api/user/write_edp1",
        headers={"Authorization": f'Bearer {user2_access_token}'},
        data=_PERMISSION_MSG,
    )
    assert response.status_code == 200

def test_user2_admin_read_edp1():
    response = test_client.get(
        "/api/admin/read_edp1",
        headers={"Authorization": f'Bearer {user2_access_token}'}
    )
    assert response.status_code == 401

def test_user2_common_write_edp1():
    response = test_client.post(
        "/api/common/write_edp1",
        headers={"Authorization": f'Bearer {user2_access_token}'},
        data=_PERMISSION_MSG,
    )
    assert response.status_code == 200


def test_user2_client_read_edp1():
    response = test_client.get(
        "/api/client/read_edp1",
        headers={"Authorization": f'Bearer {user2_access_token}'},
    )
    assert response.status_code == 401

# Admin1
def test_admin1_user_read_edp1():
    response = test_client.get(
        "/api/user/read_edp1",
        headers={"Authorization": f'Bearer {admin1_access_token}'}
    )
    assert response.status_code == 200

def test_admin1_user_write_edp1():
    response = test_client.post(
        "/api/user/write_edp1",
        headers={"Authorization": f'Bearer {admin1_access_token}'},
        data=_NO_PERMISSION_MSG,
    )
    assert response.status_code == 401

def test_admin1_admin_read_edp1():
    response = test_client.get(
        "/api/admin/read_edp1",
        headers={"Authorization": f'Bearer {admin1_access_token}'}
    )
    assert response.status_code == 200

def test_admin1_common_write_edp1():
    response = test_client.post(
        "/api/common/write_edp1",
        headers={"Authorization": f'Bearer {admin1_access_token}'},
        data=_PERMISSION_MSG,
    )
    assert response.status_code == 200


def test_admin1_client_read_edp1():
    response = test_client.get(
        "/api/client/read_edp1",
        headers={"Authorization": f'Bearer {admin1_access_token}'},
    )
    assert response.status_code == 401

# Client
def test_client_user_read_edp1():
    response = test_client.get(
        "/api/user/read_edp1",
        headers={"Authorization": f'Bearer {client_access_token}'}
    )
    assert response.status_code == 401

def test_client_user_write_edp1():
    response = test_client.post(
        "/api/user/write_edp1",
        headers={"Authorization": f'Bearer {client_access_token}'},
        data=_NO_PERMISSION_MSG,
    )
    assert response.status_code == 401

def test_client_admin_read_edp1():
    response = test_client.get(
        "/api/admin/read_edp1",
        headers={"Authorization": f'Bearer {client_access_token}'}
    )
    assert response.status_code == 401

def test_client_common_write_edp1():
    response = test_client.post(
        "/api/common/write_edp1",
        headers={"Authorization": f'Bearer {client_access_token}'},
        data=_NO_PERMISSION_MSG,
    )
    assert response.status_code == 401


def test_client_client_read_edp1():
    response = test_client.get(
        "/api/client/read_edp1",
        headers={"Authorization": f'Bearer {client_access_token}'},
    )
    assert response.status_code == 200
import requests
import json
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

username = f"user_{get_random_string(5)}"
password = "password123"
base_url = "http://127.0.0.1:8000/main"

# 1. Register
print(f"1. Registering user: {username}")
reg_resp = requests.post(f"{base_url}/register/", json={"username": username, "password": password})
print(f"Register Status: {reg_resp.status_code}")

# 2. Login
print(f"2. Logging in...")
login_resp = requests.post(f"{base_url}/login/", json={"username": username, "password": password})
print(f"Login Status: {login_resp.status_code}")

if login_resp.status_code == 200:
    token = login_resp.json().get("token")
    print(f"Token: {token}")
    
    headers = {"Authorization": f"Token {token}"}

    # 3. Get Current User
    print(f"3. Getting Current User...")
    user_resp = requests.get(f"{base_url}/current_user/", headers=headers)
    print(f"Current User Status: {user_resp.status_code}")
    print(f"Current User: {user_resp.text}")

    # 4. Post Tweet
    print(f"4. Posting Tweet...")
    tweet_resp = requests.post(f"{base_url}/tweets/", json={"content": "Hello from authenticated user!"}, headers=headers)
    print(f"Post Tweet Status: {tweet_resp.status_code}")
    print(f"Tweet: {tweet_resp.text}")
else:
    print("Login failed, skipping subsequent steps.")

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
requests.post(f"{base_url}/register/", json={"username": username, "password": password})

# 2. Login
print(f"2. Logging in...")
login_resp = requests.post(f"{base_url}/login/", json={"username": username, "password": password})

if login_resp.status_code == 200:
    token = login_resp.json().get("token")
    headers = {"Authorization": f"Token {token}"}

    # 3. Get Current User (Full Profile)
    print(f"3. Getting Full Profile...")
    user_resp = requests.get(f"{base_url}/current_user/", headers=headers)
    print(f"Profile: {user_resp.text}")

    # 4. Post a Tweet
    print(f"4. Posting Tweet...")
    requests.post(f"{base_url}/tweets/", json={"content": "My profile tweet!"}, headers=headers)

    # 5. Get User Tweets
    print(f"5. Getting User Tweets...")
    tweets_resp = requests.get(f"{base_url}/tweets/?username={username}", headers=headers)
    print(f"User Tweets: {tweets_resp.text}")
else:
    print("Login failed.")

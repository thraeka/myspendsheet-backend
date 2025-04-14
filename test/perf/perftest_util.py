from uuid import uuid4
import os
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional

USER_FILE = "perftest_user.txt"
PASSWORD = "test123"
USER_TOKEN_FILE = "perftest_user_tokens.json"
DEFAULT_NUM_OF_USERS = 5000
MAX_WORKERS = 1

def perftest_user_file_exists():
    return os.path.exists(USER_FILE)

def gen_perftest_username() -> str:
    return f"test_user_{str(uuid4())[:8]}"

def create_perftest_user(username: str) -> None:
    """ Creates perftest user in live database"""
    payload = {
        "username": username,
        "password": PASSWORD #All same pw to make easier
    }
    create_user_url = "https://api.myspendsheet.com/user/"
    try:
        resp = requests.post(create_user_url, json=payload)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Request failed: {e}")

def create_perftest_user_file(user_count: int = DEFAULT_NUM_OF_USERS) -> None:
    """Creates perftest user and writes username into user file"""
    if perftest_user_file_exists():
        raise FileExistsError(f"{USER_FILE} exists.")
    
    future_to_username = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for _ in range(user_count):
            username = gen_perftest_username()
            future = executor.submit(create_perftest_user, username)
            future_to_username[future] = username
            
    with open(USER_FILE, "w") as file:
        for future in as_completed(future_to_username):
            username = future_to_username[future]
            try:
                future.result()  # ensure no exception raised
                file.write(f"{username}\n")
            except Exception as e:
                print(f"User {username} failed to create: {e}")

def perftest_users_from_user_file(num_of_users: int = DEFAULT_NUM_OF_USERS) -> list:
    with open(USER_FILE, "r") as file:
        return [line.strip() for _, line in zip(range(num_of_users), file)]

def perftest_user_token_file_exists():
    return os.path.exists(USER_TOKEN_FILE)

def get_perftest_user_token(username) -> Optional[dict]:
    """Gets perftest user token from live database"""
    payload = {
        "username": username,
        "password": PASSWORD #All same pw to make easier
    }
    token_url = "https://api.myspendsheet.com/token/"
    try:
        resp = requests.post(token_url, json=payload)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Request failed: {e}")
    return {"access": resp.json()["access"], "refresh": resp.json()["refresh"]} 

def create_perftest_user_token_map(num_of_users: int) -> dict:
    """Create a map with {username: token} by fetching user tokens live concurrently"""
    perftest_user_token_map = {}
    # Logging for perf checking
    print(f"{num_of_users} users token fetch started at {datetime.now().strftime("%H:%M:%S")}")

    #Get usernames from user file and fetches tokens concurrently
    with open(USER_FILE, "r") as file, ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_token = {}
        for _ in range(num_of_users):
            username = file.readline().strip()
            if username == "":
                raise EOFError("Unexpected EOF. User file may not contain enough users")
            future_to_token[executor.submit(get_perftest_user_token, username)] = username

        #Get token from future and place into perftest_user_token_map
        for future in as_completed(future_to_token):
            username = future_to_token[future]
            try:
                token_resp = future.result()
            except Exception as exc:
                print(f"{username} token fetch generated exception: {exc}")
            else:
                perftest_user_token_map[username] = token_resp

        print(f"{num_of_users} users token fetch ended at {datetime.now().strftime("%H:%M:%S")}")

    return perftest_user_token_map

def create_perftest_user_token_file(num_of_users: int) -> None:
    """Create json file with {user: token} format by fetching tokens from live API"""
    if perftest_user_token_file_exists():
        os.remove(USER_TOKEN_FILE)
    perftest_user_token_map = create_perftest_user_token_map(num_of_users)
    with open(USER_TOKEN_FILE, "w") as file:
        json.dump(perftest_user_token_map, file, indent=2)

def perftest_user_token_map_from_file() -> dict:
    """Return {user:token} from perftest user token json"""
    with open(USER_TOKEN_FILE, "r") as file:
        return json.load(file)

def update_perftest_user_token_file(new_users_token_map: dict):
    """Update the user token file based on """
    # Load existing tokens
    if perftest_user_token_file_exists():
        with open(USER_TOKEN_FILE, "r") as file:
            old_users_token_maps = json.load(file)
    else:
        old_users_token_maps = {}

    # Update only changed tokens
    updated = False
    for username, new_token in new_users_token_map.items():
        if old_users_token_maps.get(username) != new_token:
            old_users_token_maps[username] = new_token
            updated = True

    # Save back only if changes occurred
    if updated:
        with open(USER_TOKEN_FILE, "w") as file:
            json.dump(new_users_token_map, file, indent=2)
        print("Token file updated with new tokens.")
    else:
        print("No token changes detected; file not updated.")


    #TODO Delete perftest user from DB

if __name__ == "__main__":
    if not perftest_user_file_exists():
        create_perftest_user_file(DEFAULT_NUM_OF_USERS)
    if perftest_user_token_file_exists():
        os.remove(USER_TOKEN_FILE)
    create_perftest_user_token_file(DEFAULT_NUM_OF_USERS)
    
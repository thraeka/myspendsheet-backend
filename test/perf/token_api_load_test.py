from locust import HttpUser, events, task
from locust.exception import StopUser
from perftest_util import perftest_users_from_user_file, perftest_user_token_map_from_file, update_perftest_user_token_file, PASSWORD
from threading import Lock

perftest_users = list()
pertest_users_token_map = dict()
perftest_users_lock = Lock()
perftest_user_token_map_lock = Lock()

@events.test_start.add_listener
def start_of_test(environment, **kwargs):
    global perftest_users, pertest_users_token_map
    perftest_users = perftest_users_from_user_file()
    pertest_users_token_map = perftest_user_token_map_from_file()

@events.test_stop.add_listener
def end_of_test(environment, **kwargs):
    update_perftest_user_token_file(pertest_users_token_map)

class SimulatedUser(HttpUser):
    def get_tokens(self):
        get_token_url = "/token/?"
        get_token_resp = self.client.post(
            get_token_url,
            json={
                "username": self.username,
                "password": PASSWORD
            }
        )
        if get_token_resp.status_code == 200:
            with perftest_user_token_map_lock:
                pertest_users_token_map[self.username] = {"access": get_token_resp.json()["access"], "refresh": get_token_resp.json()["refresh"]}
        else:
            raise StopUser("Token retreival failed")

    def on_start(self):
        with perftest_users_lock:
            self.username = perftest_users.pop()
        self.get_tokens()

    @task
    def dummy(self):
        pass
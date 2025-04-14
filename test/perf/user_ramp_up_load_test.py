from locust import HttpUser, task, between, events
from locust.exception import StopUser
from perftest_util import perftest_users_from_user_file, PASSWORD
from threading import Lock

perftest_users = []
perftest_users_lock = Lock()

@events.test_start.add_listener
def start_of_test(environment, **kwargs):
    perftest_users.extend(perftest_users_from_user_file())

class SimulatedUser(HttpUser):
    wait_time = between(25, 75)

    @task(5)
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
            self.token = get_token_resp.json()["access"]
            self.refresh = get_token_resp.json()["refresh"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            raise StopUser("Token retreival failed")

    def get_summary(self):
        get_summary_url = "/summary/2025-04-01/2025-04-12"
        get_summary_resp = self.client.get(
            get_summary_url
        )
        if get_summary_resp.status_code == 401:
            self.refresh_token()

    @task(10)
    def refresh_token(self):
        refresh_url = "/token/refresh/"
        refresh_resp = self.client.post(
            refresh_url,
            json={
                "refresh": self.refresh
            }
        )
        if refresh_resp.status_code != 200:
            raise StopUser(f"{self.username} token refresh failed")
        self.token = refresh_resp.json()["access"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(35)
    def post_txn(self):
        post_txn_url = "/txn/"
        post_txn_resp = self.client.post(
            post_txn_url,
            json={
                "date": "2025-04-10",
                "description": "Old",
                "amount": 20.00,
                "category": "Food"
            }
        )
        if post_txn_resp.status_code == 401:
            self.refresh_token()
            return
        elif post_txn_resp.status_code != 201:
            print(f"Server error: {post_txn_resp.status_code}")
            return
        self.txn_id_posted.append(post_txn_resp.json()["id"])
        self.get_summary()


    @task(15)
    def delete_txn(self):
        if not self.txn_id_posted:
            return
        txn_id = self.txn_id_posted.pop()
        del_txn_url = f"/txn/{txn_id}/"
        del_txn_resp = self.client.delete(
            del_txn_url
        )
        if del_txn_resp.status_code == 401:
            self.refresh_token()
            return
        self.get_summary()

    @task(25)
    def patch_txn(self):
        if not self.txn_id_posted:
            return
        txn_id = self.txn_id_posted[len(self.txn_id_posted)-1]
        patch_txn_url = f"/txn/{txn_id}/"
        patch_txn_resp = self.client.patch(
            patch_txn_url,
            json={
                "date": "2025-04-11",
                "description": "New",
                "amount": 14.24,
                "category": "Restaurants"
            }
        )
        if patch_txn_resp.status_code == 401:
            self.refresh_token()
            return
        self.get_summary()

    @task(10)
    def get_txn_list(self):
        if not self.txn_id_posted:
            return
        txn_list_url = f"/txn/?start_date=2025-04-01&end_date=2025-04-12"
        txn_list_resp = self.client.get(
            txn_list_url,
        )
        if txn_list_resp.status_code == 401:
            self.refresh_token()

    def on_start(self):
        self.txn_id_posted = []
        with perftest_users_lock:
            self.username = perftest_users.pop()
        self.get_tokens()
        self.get_txn_list()
        self.get_summary()

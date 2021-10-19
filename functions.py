import json
import string
import random

from locust import HttpUser, constant, SequentialTaskSet, task


# Define all tasks in task set
def id_generator(size=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class Function(SequentialTaskSet):
    # Constant(wait_time), Constant_pacing(wait_time), between(min, max),
    # These function inject time b/w tasks
    wait_time = constant(1)

    # token_string = ""
    def __init__(self, parent):
        print("init function \n")
        super().__init__(parent)
        self.token_string = ""
        self.org_id = ""
        self.app_id = ""
        self.func_name = ""
        self.headers = {}

    def on_start(self):
        print("On Start \n")
        self.token_string, self.org_id = self.login_user()
        # print("Token -->", self.token_string)
        # print("\n OrgID -->", self.org_id)
        self.headers = {
            'Authorization': 'Bearer ' + self.token_string,
            'Accept': 'application/ion+json',
            "Content-Type": "application/json"
        }

    def login_user(self):
        response = self.client.post("/guest/login", json=
        {
            "email": "edjperformance@mailinator.com",
            "password": "Hello@123"
        }
                                    )
        # fetch token and org
        json_var = response.json()

        organizations = json_var["organizations"]
        org_id = organizations[0]["id"]
        return json_var["token"], org_id

    @task
    def read_applications(self):
        response = self.client.get(
            "/api/applications?limit=1",
            headers=self.headers
        )
        print("Read application")
        # print("\n response: " + response.text)
        # json_var = response.json()
        # print("\n applications: " + str(json_var))

    @task
    def create_applications(self):
        random_name = id_generator(3)
        payload = json.dumps({
            "name": random_name,
            "organization": "" + self.org_id + "",
            "status": "active"
        })
        print("Create Application")
        response = self.client.post("/api/applications", headers=self.headers, data=payload)
        json_var = response.json()
        self.app_id = json_var["id"]
        print("\n appID: " + self.app_id)

    @task
    def create_deploy_functions(self):
        random_name = id_generator(4)

        # Create
        payload = json.dumps({
            "name": random_name,
            "properties": {
                "language": "rust",
                "memoryAllocated": 134217728,
                "runtime": "wasm",
                "timeout": 30000,
                "trigger": "http"
            },
            "policies": []
        })
        print("Create function")
        response = self.client.post("/api/applications/" + self.app_id + "/deployments",
                                    headers=self.headers,
                                    data=payload)
        json_var = response.json()
        # print("Create func" + response.text)
        self.func_name = json_var["name"]

        deploy_section = json_var["deploy"]
        update_section = json_var["update"]
        deploy_url = deploy_section["href"]
        callback_url = update_section["href"]

        print("\n func_name: " + self.func_name)
        print("\n deploy url: " + deploy_url)
        print("\n callback url: " + callback_url)

        # deploy
        print("Deployment")
        filename = 'hello_world.wasm'
        payload = {'peer-addrs': '',
                   'notary': 'false',
                   'callBackURL': callback_url
                   }
        files = [
            ('content', (filename, open(filename, 'rb'),
                         'application/octet-stream'))
        ]
        headers = {
            'Authorization': 'Bearer ' + self.token_string
        }

        response = self.client.put(deploy_url, headers=headers, data=payload, files=files)
        # json_var = response.json()
        print("Deployment response -> : " + response.text)

   # @task
    def delete_applications(self):
        print("delete applications")
        response = self.client.delete("/api/applications/" + self.app_id, headers=self.headers)
        json_var = response.json()
        print("\n delete response: " + str(json_var))


# Define user/ httpuser to trigger and execute functionperf class
class TaskExecutor(HttpUser):
    host = "https://api.load.edjx.network"
    tasks = [Function]

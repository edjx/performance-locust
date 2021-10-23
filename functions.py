import json
import string
import random
import time

from locust import HttpUser, SequentialTaskSet, task, constant, tag


# Define all tasks in task set
def id_generator(size=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class Function(SequentialTaskSet):
    # Constant(wait_time), Constant_pacing(wait_time), between(min, max),
    # These function inject time b/w tasks
    wait_time = constant(2)

    def __init__(self, parent):
        print("init function \n")
        super().__init__(parent)
        self.token_string = ""
        self.org_id = ""
        self.app_id = ""
        self.func_name = ""
        self.func_execute_url = ""
        self.headers = {}

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

    def read_applications(self):
        response = self.client.get(
            "/api/applications?limit=1",
            headers=self.headers
        )
        print("Read application")
        # print("\n response: " + response.text)
        # json_var = response.json()
        # print("\n applications: " + str(json_var))

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
        return json_var["id"]
        # print("\n appID: " + self.app_id)

    def create_deploy_functions(self, app_id):
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
        response = self.client.post("/api/applications/" + app_id + "/deployments",
                                    headers=self.headers,
                                    data=payload)
        json_var = response.json()
        func_name = json_var["name"]

        deploy_section = json_var["deploy"]
        update_section = json_var["update"]
        deploy_url = deploy_section["href"]
        callback_url = update_section["href"]

        # print("\n func_name: " + self.func_name)
        # print("\n deploy url: " + deploy_url)
        # print("\n callback url: " + callback_url)

        # deploy
        print("Deploy function")
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
        json_var = response.json()
        status = json_var["status"]
        assert status == "accepted"
        print(func_name + " :is Deployed")
        return func_name

    def get_url_from_function(self, app_id, func_name):
        print("Get execute URL from function" + func_name)
        response = self.client.get("/api/applications/" + app_id + "/functions/" + func_name,
                                   headers=self.headers)
        json_var = response.json()
        # print("get_url_from_function response" + response.text)
        execute = json_var["execute"]
        execute_url = execute["href"]
        return execute_url

    def delete_applications(self, app_id):
        print("delete applications")
        response = self.client.delete("/api/applications/" + app_id, headers=self.headers)
        json_var = response.json()
        print("\n delete response: " + str(json_var))

    def delete_function(self, app_id, func_name):
        print("delete applications")
        response = self.client.delete("/api/applications/" + app_id + "/functions/" + func_name,
                                      headers=self.headers)
        json_var = response.json()
        print("\n delete response: " + str(json_var))

    def on_start(self):
        print("On Start \n")
        self.token_string, self.org_id = self.login_user()
        # print("\n OrgID -->", self.org_id)
        self.headers = {
            'Authorization': 'Bearer ' + self.token_string,
            'Accept': 'application/ion+json',
            "Content-Type": "application/json"
        }

        # self.app_id = self.create_applications()
        # self.func_name = self.create_deploy_functions(self.app_id)
        # self.func_execute_url = self.get_url_from_function(self.app_id, self.func_name)
        # print("func URL -> " + self.func_execute_url)

    @tag('exe_func')
    @task
    def function_executor(self):
        func_url = "https://c64394df-f664-4f43-8c56-99a4c895417e.fn.load.edjx.network/IXT2"
        response = self.client.get(func_url)
        assert response.text == "Hello World"

    @tag('e2e')
    @task
    def e2e_function_executor(self):
        app_id = self.create_applications()
        func_name = self.create_deploy_functions(app_id)
        # time.sleep(2)
        func_execute_url = self.get_url_from_function(app_id, func_name)
        response = self.client.get(func_execute_url)
        assert response.text == "Hello World"
        self.delete_function(app_id, func_name)
        self.delete_applications(app_id)
        # time.sleep(2)

    # def on_stop(self):
    #     self.delete_applications(self.app_id)


# Define user/ httpuser to trigger and execute functionperf class
class TaskExecutor(HttpUser):
    host = "https://api.load.edjx.network"
    tasks = [Function]

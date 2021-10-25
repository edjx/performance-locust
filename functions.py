import json
import string
import random
import time
from urllib import request

import requests
from locust import HttpUser, SequentialTaskSet, task, constant, tag, TaskSet

# Define all tasks in task set
from requests import get


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
        },
                                    name='Login')
        # fetch token and org
        json_var = response.json()

        organizations = json_var["organizations"]
        org_id = organizations[0]["id"]
        return json_var["token"], org_id

    def read_applications(self):
        response = self.client.get(
            "/api/applications?limit=1",
            headers=self.headers,
            name='Read Applications')
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
        response = self.client.post("/api/applications", name='Create Application', headers=self.headers, data=payload)
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
                                    name='Create Function',
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

        response = self.client.put(deploy_url,name='Deploy Function', headers=headers, data=payload, files=files)
        json_var = response.json()
        status = json_var["status"]
        assert status == "accepted"
        print(func_name + " :is Deployed")
        return func_name

    def get_url_from_function(self, app_id, func_name):
        print("Get execute URL from function" + func_name)
        response = self.client.get("/api/applications/" + app_id + "/functions/" + func_name,
                                   name='Read Function', headers=self.headers)
        json_var = response.json()
        # print("get_url_from_function response" + response.text)
        execute = json_var["execute"]
        execute_url = execute["href"]
        return execute_url

    def delete_applications(self, app_id):
        print("delete applications")
        response = self.client.delete("/api/applications/" + app_id, name='Delete Application', headers=self.headers)
        json_var = response.json()
        print("\n delete response: " + str(json_var))

    def delete_function(self, app_id, func_name):
        print("delete applications")
        response = self.client.delete("/api/applications/" + app_id + "/functions/" + func_name,
                                      name='Delete Function',
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

    @tag('e2e')
    @task
    def e2e_function_executor(self):
        app_id = self.create_applications()
        func_name = self.create_deploy_functions(app_id)
        # time.sleep(2)
        func_execute_url = self.get_url_from_function(app_id, func_name)
        response = self.client.get(func_execute_url, name='Function Executor',)
        assert response.text == "Hello World"
        self.delete_function(app_id, func_name)
        self.delete_applications(app_id)
        # time.sleep(2)

    # def on_stop(self):
    #     self.delete_applications(self.app_id)


class Resources(TaskSet):

    def get_geohash(self, location):
        geohash = {'India': ['ttrkr', 'tdqfr', 'tepeu', 'ttnfyr', 'ttp52'],
                   # near Delhi, banglore, hyderabad, shashtri, airforce
                   'US': ['9q8yy', 'dr5ru', 'dqcjr', 'c22zr'],  # sanFran, NYC, washington, seattle
                   'Global': ['gc6m2', 'gcpuv', 'u4xez', 'sycu2', 'tzhuv', 'w68nr'],
                   # ireland, UK, norway, turkey, china, thailand
                   '134.122.3.240': 'New York',
                   }
        return geohash[location]

    def get_current_node(self, ip_address):
        load_nodes = {'64.227.186.81': 'Banglore',
                      '64.227.176.181': 'Banglore',
                      '167.71.183.84': 'New York',
                      '134.122.3.240': 'New York',
                      '137.184.10.253': 'San Francisco',
                      '164.90.145.242': 'San Francisco',
                      '137.184.10.173': 'San Francisco',
                      '165.232.129.105': 'San Francisco'
                      }
        return load_nodes[ip_address]

    @tag('exe_func')
    @task
    def function_executor(self):
        # https://60ede549-9b58-4245-a2cf-0e929fe341f2--ttrkr.fn.load.edjx.network/HelloWorld
        uuid = "60ede549-9b58-4245-a2cf-0e929fe341f2"
        const_host = ".fn.load.edjx.network"
        func_name = "/HelloWorld"
        # geohash = random.choice(['ttrkr', '9q8yy', '9q8yw', '9q8yq', '9q8ym', 'dr5ru', 'tdr1v'])
        # geohash = 'ttqds'
        geohash = random.choice(self.get_geohash('US'))

        func_url = "https://" + uuid + "--" + geohash + const_host + func_name
        # print('URL->' + func_url)
        with self.client.get(func_url, catch_response=True, name='Function Executor', stream=True) as response:
            remote_address, port = response.raw._connection.sock.getpeername()
            print('\nURL: ' + func_url)
            print('Serving Node: ' + remote_address + ' (' + self.get_current_node(remote_address) + ')\n')
            assert response.text == "Hello World"

        # Define user/ httpuser to trigger and execute functionperf class


class TaskExecutor(HttpUser):
    host = "https://api.load.edjx.network"
    tasks = [Function]

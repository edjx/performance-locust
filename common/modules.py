# This file contains all reusable functions
import json

from common.utils import *


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

    response = self.client.put(deploy_url, name='Deploy Function', headers=headers, data=payload, files=files)
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

# This file contains all reusable functions
import json
import logging

from common.utils import *


def login_user(self):
    response = self.client.post("/guest/login", json=
    {
        "email": "manualtest2@mailinator.com",
        "password": "Hello@123"
    },
                                name='Login')
    # fetch token and org
    json_var = response.json()

    organizations = json_var["organizations"]
    org_id = organizations[1]["id"]
    return json_var["token"], org_id


# ******* All things Applications *******#

def read_all_applications(self):
    logging.info("Read applications")
    with self.client.get("/api/applications?limit=1", headers=self.headers,
                         name='Read Applications') as response:
        response.status_code = 200
    # print("\n response: " + response.text)


def create_applications(self, org_id):
    random_name = id_generator(3)
    payload = json.dumps({
        "name": random_name,
        "organization": "" + org_id + "",
        "status": "active"
    })
    print("Create Application")
    response = self.client.post("/api/applications", name='Create Application', headers=self.headers, data=payload)
    json_var = response.json()
    # print(response.text)
    return json_var["id"]


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
    # logging.info("\n Create function response: %s", response.content)
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
    # logging.info("\n\n Deploy function response: %s", response.content)
    status = json_var["status"]
    assert status == "accepted"
    # print(func_name + " :is Deployed")
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


# ******* All things Buckets *******#

def create_bucket(self, org_id):
    logging.info("Create bucket")
    random_name = "load_" + id_generator(3)
    payload = json.dumps({
        "name": random_name,
        "organization": "" + org_id + "",
        "description": "from load scripts",
        "isPublic": "true"
    })
    response = self.client.post("/api/buckets", name='Create Bucket', headers=self.headers, data=payload)
    json_var = response.json()
    # print("bucket create response: ", response.text)
    return json_var["id"]


def delete_bucket(self, bucket_id):
    logging.info("Delete bucket")
    response = self.client.delete("/api/buckets/" + bucket_id, name='Delete Bucket', headers=self.headers)
    json_var = response.json()
    print("\n delete response: " + str(json_var))


def upload_file(self, bucket_id):
    logging.info("Create file")
    random_name = "loadfile_" + id_generator(3)
    payload = json.dumps({
        "bucket": bucket_id,
        "name": random_name,
        "properties": [
            {
                "key": "Content-Type",
                "value": "image/jpeg"
            }
        ]
    })

    # Create file
    response = self.client.post("/api/buckets/" + bucket_id + "/uploads",
                                name='Create File',
                                headers=self.headers,
                                data=payload)
    json_var = response.json()
    # logging.info("\n Create file response: %s", response.content)
    file_name = json_var["name"]

    # Get upload and call back url
    upload_section = json_var["upload"]
    callback_url = json_var["href"]
    upload_url = upload_section["href"]

    # Upload file
    logging.info("Uploading file")
    filename = 'edjqa-logo.png'
    payload = {
        'callBackURL': callback_url
    }
    files = [
        ('content', (filename, open(filename, 'rb'),
                     'image/png'))
    ]
    headers = {
        'Authorization': 'Bearer ' + self.token_string
    }
    response = self.client.put(upload_url, name='Upload File', headers=headers, data=payload, files=files)
    json_var = response.json()
    status = json_var["status"]
    # print("Upload file response", response.content)
    # logging.info("\n Upload file response: %s", response.content)
    assert status == "accepted"

    print(file_name + " : File is uploaded")
    return file_name


def get_url_from_file(self, bucket_id, file_name):
    print("Get download URL from file: " + file_name)
    response = self.client.get("/api/buckets/" + bucket_id + "/files/" + file_name,
                               name='Read File', headers=self.headers)
    json_var = response.json()
    # print("get_url_from_function response" + response.text)
    download_url = json_var["url"]
    return download_url


def delete_file(self, bucket_id, file_name):
    logging.info("Delete File")
    with self.client.delete("/api/buckets/" + bucket_id + "/files/" + file_name,
                            name='Delete File', headers=self.headers) as response:
        assert response.status_code == 200
        json_var = response.json()
        print("\n delete response: " + str(json_var))

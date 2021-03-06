# This file contains all reusable functions
import json
import logging

from common.utils import *


def login_user(self):
    response = self.client.post("/guest/login", json=
    {
        "email": "edjperformance@mailinator.com",
        "password": "Hello@123"
    },
                                name='Login')
    # status_code = response.status_code
    if response.status_code == 201:
        logging.info("User logged in")
        # fetch token and org
        json_var = response.json()

        organizations = json_var["organizations"]
        org_id = organizations[0]["id"]
        return json_var["token"], org_id
    else:
        logging.info("Unable to login: %s", response.content)

    # ******* All things Applications *******#


def read_all_applications(self):
    logging.info("List Applications")
    with self.client.get("/api/applications?limit=50", headers=self.headers,
                         name='List Applications') as response:
        response.status_code = 200
    # print("\n response: " + response.text)


def read_application(self, app_id):
    logging.info("Read Application")
    with self.client.get("/api/applications/" + app_id, headers=self.headers,
                         name='List Applications') as response:
        response.status_code = 200


def update_application(self, app_id):
    random_name = id_generator(3)
    payload = json.dumps({
        "name": random_name + "afterUpdate",
        "status": "active"
    })

    logging.info("Update Application")
    with self.client.put("/api/applications/" + app_id, headers=self.headers,
                         name='Update Application', data=payload) as response:
        # print(response.text)
        response.status_code = 200


def create_applications(self, org_id):
    random_name = id_generator(3)
    payload = json.dumps({
        "name": random_name,
        "organization": "" + org_id + "",
        "status": "active"
    })
    logging.info("Create Application")
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
    logging.info("Create function")
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
    logging.info("Deploy function")
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
    logging.info("Get execute URL from function %s", func_name)
    response = self.client.get("/api/applications/" + app_id + "/functions/" + func_name,
                               name='Read Function', headers=self.headers)
    json_var = response.json()
    # print("get_url_from_function response" + response.text)
    execute = json_var["execute"]
    execute_url = execute["href"]
    return execute_url


def delete_applications(self, app_id):
    logging.info("Delete Application")
    response = self.client.delete("/api/applications/" + app_id, name='Delete Application', headers=self.headers)
    # json_var = response.json()
    # logging.info("\n Delete application response: %s", str(json_var))
    response.status_code = 200


def delete_function(self, app_id, func_name):
    logging.info("Delete Function")
    response = self.client.delete("/api/applications/" + app_id + "/functions/" + func_name,
                                  name='Delete Function',
                                  headers=self.headers)
    json_var = response.json()
    logging.info("\n Delete function response: %s", str(json_var))


def execute_function_url(self, func_url):
    with self.client.get(func_url, catch_response=True, name='Function Executor', stream=True) as response:
        remote_address, port = response.raw._connection.sock.getpeername()
        logging.info('URL: %s', func_url)
        logging.info('Serving Node: ' + remote_address + ' (' + get_current_node(remote_address) + ')\n')
        return response


# ******* All things Buckets *******#

def create_bucket(self, org_id):
    logging.info("Create Bucket")
    random_name = "load_" + id_generator(3)
    payload = json.dumps({
        "name": random_name,
        "organization": "" + org_id + "",
        "description": "from load scripts",
        "isPublic": "true"
    })
    response = self.client.post("/api/buckets", name='Create Bucket', headers=self.headers, data=payload)
    json_var = response.json()
    # bucket_name = json_var["name"]
    # logging.info("%s :Bucket is Created", bucket_name)
    # print("bucket create response: ", response.text)
    return json_var["id"]


def delete_bucket(self, bucket_id):
    logging.info("Delete Bucket")
    response = self.client.delete("/api/buckets/" + bucket_id, name='Delete Bucket', headers=self.headers)
    json_var = response.json()
    # logging.info("\n Delete bucket response: %s", str(json_var))


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

    logging.info("%s :File is uploaded", file_name)
    return file_name


def get_url_from_file(self, bucket_id, file_name):
    logging.info("Get download URL from file: %s", file_name)
    response = self.client.get("/api/buckets/" + bucket_id + "/files/" + file_name,
                               name='Read File', headers=self.headers)
    json_var = response.json()
    # logging.info("\n Get Url from file: %s", response.content)
    download_url = json_var["url"]
    return download_url


def delete_file(self, bucket_id, file_name):
    logging.info("Delete File")
    with self.client.delete("/api/buckets/" + bucket_id + "/files/" + file_name,
                            name='Delete File', headers=self.headers) as response:
        assert response.status_code == 200
        json_var = response.json()
        logging.info("\n Delete file response: %s", str(json_var))


def download_file(self, download_url):
    with self.client.get(download_url, name='File Download') as response:
        assert response.status_code == 200
        # print("download URL response -->", response.status_code)
        logging.info("file downloaded successfully")


def read_bucket(self, bucket_id):
    logging.info("Read Bucket")
    with self.client.get("/api/buckets/" + bucket_id, headers=self.headers,
                         name='Read Bucket') as response:
        response.status_code = 200


def update_bucket(self, bucket_id):
    random_name = id_generator(3)
    payload = json.dumps({
        "name": random_name + "afterUpdate",
        "description": "from Locust load"
    })

    logging.info("Update Bucket")
    with self.client.put("/api/buckets/" + bucket_id, headers=self.headers,
                         name='Update Bucket', data=payload) as response:
        # print(response.text)
        response.status_code = 200


def read_all_buckets(self):
    logging.info("List Buckets")
    with self.client.get("/api/buckets?limit=50", headers=self.headers,
                         name='List Buckets') as response:
        response.status_code = 200
    # print("\n response: " + response.text)

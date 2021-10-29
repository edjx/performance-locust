import json
import logging
import string
import random
import time
import traceback
import urllib

from common.modules import *
from common.utils import *
import requests
from locust import HttpUser, SequentialTaskSet, task, constant, tag, TaskSet, between

# Define all tasks in task set
from requests import get


class Function(SequentialTaskSet):
    # Constant(wait_time), Constant_pacing(wait_time), between(min, max),
    # These function inject time b/w tasks
    wait_time = between(2, 4)

    def __init__(self, parent):
        print("init function \n")
        super().__init__(parent)
        self.token_string = ""
        self.org_id = ""
        self.app_id = ""
        self.func_name = ""
        self.bucket_id = ""
        self.func_execute_url = ""
        self.headers = {}

    def on_start(self):
        print("On Start \n")
        self.token_string, self.org_id = login_user(self)
        # print("\n OrgID -->", self.org_id)
        self.headers = {
            'Authorization': 'Bearer ' + self.token_string,
            'Accept': 'application/ion+json',
            "Content-Type": "application/json"
        }

        # Create Application and Bucket
        self.app_id = create_applications(self, self.org_id)
        self.bucket_id = create_bucket(self, self.org_id)

    @tag('e2e_function')
    @task
    def e2e_function_executor(self):
        try:
            read_all_applications(self)
            func_name = create_deploy_functions(self, self.app_id)
            func_execute_url = get_url_from_function(self, self.app_id, func_name)
            logging.info("Func Exe URL: %s", func_execute_url)
            time.sleep(1)
            response = self.client.get(func_execute_url, name='Function Executor', )
            assert response.text == "Hello World"
            # delete_function(self, self.app_id, func_name)
        except Exception as e:
            traceback.print_exc()
            print("Exception occured: ", e)

    @tag('e2e_bucket')
    @task
    def e2e_file_upload(self):
        try:
            filename = upload_file(self, self.bucket_id)
            download_url = get_url_from_file(self, self.bucket_id, filename)
            logging.info("File download url: %s", download_url)

            # Download file
            time.sleep(1)
            with self.client.get(download_url, name='File Download') as response:
                assert response.status_code == 200
                # print("download URL response -->", response.status_code)
                logging.info("file downloaded successfully")
        except Exception as e:
            traceback.print_exc()
            print("Exception occured: ", e)

        # Delete resources
        # delete_file(self, self.bucket_id, filename)

    def on_stop(self):
        if len(self.app_id) != 0:
            delete_applications(self, self.app_id)

        if len(self.bucket_id) != 0:
            delete_bucket(self, self.bucket_id)


class Resources(TaskSet):

    @tag('exe_func')
    @task
    def function_executor(self):
        # https://60ede549-9b58-4245-a2cf-0e929fe341f2--ttrkr.fn.load.edjx.network/HelloWorld
        uuid = "60ede549-9b58-4245-a2cf-0e929fe341f2"
        const_host = ".fn.load.edjx.network"
        func_name = "/HelloWorld"
        # geohash = 'ttqds'
        geohash = random.choice(get_geohash('Global'))

        func_url = "https://" + uuid + "--" + geohash + const_host + func_name
        # print('URL->' + func_url)
        with self.client.get(func_url, catch_response=True, name='Function Executor', stream=True) as response:
            remote_address, port = response.raw._connection.sock.getpeername()
            print('\nURL: ' + func_url)
            print('Serving Node: ' + remote_address + ' (' + get_current_node(remote_address) + ')\n')
            assert response.text == "Hello World"


class TaskExecutor(HttpUser):
    host = "https://api.load.edjx.network"
    tasks = [Function]

import json
import logging
import string
import random
from common.modules import *
from common.utils import *
import requests
from locust import HttpUser, SequentialTaskSet, task, constant, tag, TaskSet

# Define all tasks in task set
from requests import get


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

    def on_start(self):
        print("On Start \n")
        self.token_string, self.org_id = login_user(self)
        # print("\n OrgID -->", self.org_id)
        self.headers = {
            'Authorization': 'Bearer ' + self.token_string,
            'Accept': 'application/ion+json',
            "Content-Type": "application/json"
        }

    @tag('e2e_function')
    @task
    def e2e_function_executor(self):
        app_id = create_applications(self, self.org_id)
        func_name = create_deploy_functions(self, app_id)
        func_execute_url = get_url_from_function(self, app_id, func_name)

        response = self.client.get(func_execute_url, name='Function Executor', )
        assert response.text == "Hello World"

        delete_function(self, app_id, func_name)
        delete_applications(self, app_id)

    @tag('e2e_bucket')
    @task
    def e2e_file_upload(self):
        bucket_id = create_bucket(self, self.org_id)
        # print("id -->", bucket_id)
        upload_file(self, bucket_id)
        delete_bucket(self, bucket_id)

    # def on_stop(self):
    #     self.delete_applications(self.app_id)


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
    tasks = [Function, Resources]

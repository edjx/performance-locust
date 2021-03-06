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


class LoadE2E(SequentialTaskSet):

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
        logging.info("On Start \n")
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
            response = self.client.get(func_execute_url, name='Function Executor')
            assert response.text == "Hello World"
            # delete_function(self, self.app_id, func_name)
        except Exception as e:
            traceback.print_exc()
            logging.exception("Exception occurred: %s", e)
        self.interrupt(reschedule=False)  # To exit execution so that other class can pick

    @tag('e2e_bucket')
    @task
    def e2e_file_upload(self):
        try:
            # self.bucket_id = "9e5d0108-cae7-492e-adad-1e6c93bbec4e"
            filename = upload_file(self, self.bucket_id)
            time.sleep(1)  # wait for data updation
            download_url = get_url_from_file(self, self.bucket_id, filename)
            logging.info("File download url: %s", download_url)
            download_file(self, download_url)
        except Exception as e:
            traceback.print_exc()
            logging.exception("Exception occurred: %s", e)

        # Delete resources
        # delete_file(self, self.bucket_id, filename)
        self.interrupt(reschedule=False)

    def on_stop(self):
        if len(self.app_id) != 0:
            delete_applications(self, self.app_id)

        if len(self.bucket_id) != 0:
            delete_bucket(self, self.bucket_id)


class DirectLoad(TaskSet):

    @tag('executor')
    @task
    def function_executor(self):
        # https://60ede549-9b58-4245-a2cf-0e929fe341f2.fn.load.edjx.network/HelloWorld
        uuid = "60ede549-9b58-4245-a2cf-0e929fe341f2"
        const_host = ".fn.load.edjx.network"
        func_name = "/HelloWorld"
        # geohash = 'ttqds'
        geohash = random.choice(get_geohash('Global'))

        func_url = "https://" + uuid + "--" + geohash + const_host + func_name
        # print('URL->' + func_url)
        print("\n[FUNCTION EXECUTOR]")
        response = execute_function_url(self, func_url)

        assert response.text == "Hello World"
        self.interrupt(reschedule=False)  # To exit execution so that other class can pick

    @tag('cdn')
    @task
    def cdn_executor(self):
        url = "http://xyz.mishyan.com/"
        with self.client.get(url, catch_response=True, name='CDN', stream=True) as response:
            assert response.status_code == 200
            assert response.headers.get('Server') == "EDJX"
            remote_address, port = response.raw._connection.sock.getpeername()
            print("\n[CDN]")
            logging.info("URL: %s", url)
            logging.info("URL response code: %s", response.status_code)
            logging.info('Serving Node: ' + remote_address + ' (' + get_current_node(remote_address) + ')')
            logging.info("X-Cache-Status: %s \n", response.headers.get('X-Cache-Status'))
        self.interrupt(reschedule=False)  # To exit execution so that other class can pick

    # @tag('files')
    # @task
    # def file_upload_download(self):
    #     bucket_id = "9e5d0108-cae7-492e-adad-1e6c93bbec4e"
    #
    #     filename = upload_file(self, bucket_id)
    #     download_url = get_url_from_file(self, bucket_id, filename)
    #     logging.info("File download url: %s", download_url)
    #     time.sleep(1)
    #     download_file(self,download_url)
    #     # Delete resources
    #     # delete_file(self, bucket_id, filename)


class Edjapi(TaskSet):

    # Global variable for test
    def __init__(self, parent):
        print("init function \n")
        super().__init__(parent)
        self.token_string = ""
        self.org_id = ""
        self.headers = {}

    # Pre test
    def on_start(self):
        logging.info("On Start \n")
        self.token_string, self.org_id = login_user(self)
        # print("\n OrgID -->", self.org_id)
        self.headers = {
            'Authorization': 'Bearer ' + self.token_string,
            'Accept': 'application/ion+json',
            "Content-Type": "application/json"
        }

    @tag('app_crud')
    @task
    def application(self):
        app_id = create_applications(self, self.org_id)
        read_application(self, app_id)
        update_application(self, app_id)
        delete_applications(self, app_id)
        read_all_applications(self)
        self.interrupt(reschedule=False)  # To exit execution so that other class can pick

    @tag('buk_crud')
    @task
    def buckets(self):
        bucket_id = create_bucket(self, self.org_id)
        read_bucket(self, bucket_id)
        update_bucket(self, bucket_id)
        delete_bucket(self, bucket_id)
        read_all_buckets(self)
        self.interrupt(reschedule=False)  # To exit execution so that other class can pick


class TaskExecutor(HttpUser):
    tasks = [LoadE2E, DirectLoad, Edjapi]
    # Constant(wait_time), Constant_pacing(wait_time), between(min, max),
    # These function inject time b/w tasks
    wait_time = between(2, 4)

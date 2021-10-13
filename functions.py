from locust import HttpUser, task, constant, TaskSet


# Define all tasks in task set
class Function(TaskSet):
    # token_string = ""
    def __init__(self, parent):
        super().__init__(parent)
        self.token_string = ""
        self.org_id = ""

    @task
    def login_user(self):
        response = self.client.post("/guest/login", json=
        {
            "email": "testedjx@mailinator.com",
            "password": "Hello@123!"
        }
                                    )

        print("Task 1")
        # fetch token
        json_var = response.json()
        self.user.token_string = json_var["token"]
        # print("\n token: " + self.user.token_string)

        # fetch orgid
        organizations = json_var["organizations"]
        self.user.org_id = organizations[0]["id"]
        # print("\n orgID: " + org_id)

    @task
    def read_applications(self):
        response = self.client.get(
            "/api/applications?limit=1",
            headers={"authorization": "Token " + self.user.token_string}
        )
        print("Task 2")
        # print("\n token: " + self.user.token_string)
        # print("\n response: " + response.text)
        json_var = response.json()
        # print("\n applications: " + str(json_var))

        # print(self.user.org_id)

    @task
    def create_applications(self):
        response = self.client.post("/api/applications",
                                    headers={"authorization": "Token " + self.user.token_string},
                                    json={
                                        "organization": '"' + self.user.org_id + '"',
                                        "name": "performance",
                                        "status": "active"
                                    }
                                    )
        print("Task 3")
        # print("\n token: " + self.user.token_string)
        print("\n response: " + response.text)
        # json_var = response.json()
        # print("\n applications: " + str(json_var))

        print(self.user.org_id)


# Define user/ httpuser to trigger and execute functionperf class
class TaskExecutor(HttpUser):
    host = "https://api.load.edjx.network"
    tasks = [Function]
    wait_time = constant(1)

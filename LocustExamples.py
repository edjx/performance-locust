# To start the test locust either needs 'user' class or 'httpuser' class

from locust import User, task, constant


class MyFirstTest(User):
    weight = 2 # probability of picking up this class for the test
    wait_time = constant(1)  # breath time for 1 second

    @task
    def launch(self):
        print("Launch the url")

    @task
    def search(self):
        print("Searching")


class MySecondTest(User):
    weight = 2
    wait_time = constant(1)

    @task
    def launch(self):
        print("Second Test")

    @task
    def search(self):
        print("Searching again")

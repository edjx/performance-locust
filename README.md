# Performance Locust

This is a side project created for putting quick load using tool [Locust](https://github.com/locustio/locust).

Language: Python

### Setup and run from Web UI
- Install locust ```pip3 install locust```
- Validate Installations ```locust -V```
- Clone project
- Run ```locust -f load_tests.py --tags buk_crud```
- Open UI: ```http://localhost:8089```
- Enter No. of users, spawn rate and Run
- Bucket Crud test should run


### Availble Load Scripts

Run tests in headless mode with given time frame
```
# application crud
locust -f load_tests.py --tags buk_crud --headless -u 1 -r 1 --run-time 10s

# bucket crud
locust -f load_tests.py --tags app_crud --headless -u 1 -r 1 --run-time 10s

# e2e functions
locust -f load_tests.py --tags e2e_function --headless -u 1 -r 1 --run-time 10s

# e2e bucket
locust -f load_tests.py --tags e2e_bucket --headless -u 1 -r 1 --run-time 10s

# function executor with geo hash
locust -f load_tests.py --tags executor --headless -u 1 -r 1 --run-time 10s

# load on HTTP URL
locust -f load_tests.py --tags cdn --headless -u 1 -r 1 --run-time 10s
```


### Quick Read for Analysis
* Request — Total number of requests made so far
* Fails — Number of requests that have failed
* Median — Response speed for 50 percentile in ms
* 90%ile — Response speed for 90 percentile in ms
* Average — Average response speed in ms
* Min — Minimum response speed in ms
* Max — Maximum response speed in ms
* Average bytes — Average response size in bytes
* Current RPS — Current requests per second
* Current Failure/s — Total number of failures per second


### References:
https://locust.io/

http://docs.locust.io/en/stable/


### Authors: 

@edjx/qa

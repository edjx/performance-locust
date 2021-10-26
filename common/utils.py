import string
import random


def id_generator(size=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def get_geohash(location):
    geohash = {'India': ['ttrkr', 'tdqfr', 'tepeu', 'ttnfyr', 'ttp52'],
               # near Delhi, banglore, hyderabad, shashtri, airforce
               'US': ['9q8yy', 'dr5ru', 'dqcjr', 'c22zr'],  # sanFran, NYC, washington, seattle
               'Global': ['gc6m2', 'gcpuv', 'u4xez', 'sycu2', 'tzhuv', 'w68nr'],
               # ireland, UK, norway, turkey, china, thailand
               '134.122.3.240': 'New York',
               }
    return geohash[location]


def get_current_node(ip_address):
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

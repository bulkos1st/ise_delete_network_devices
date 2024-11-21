#!/usr/bin/env python

"""
run as python ise_delete_network_device.py -U <username> -F devices.txt

#devices.txt
devicea
deviceb
switcha
switchb

"""

import argparse
from datetime import datetime
import getpass
import os
import sys
from ciscoisesdk import IdentityServicesEngineAPI
from ciscoisesdk.exceptions import ApiError

SCRIPT_VERSION = 1.0
BASE_URL = 'enter_ise_url_here'
SEPARATOR = 40 * "-"

# Parse CLI input
my_parser = argparse.ArgumentParser(description='Delete ISE network device', epilog='Enjoy the program! :)')
my_parser.add_argument('-U', '--username', metavar='<username>', type=str, help='Username used to login to ISE')
my_parser.add_argument('-F', '--file', metavar='<file name>', type=str, help='File with devices(one column of hostnames)')
my_parser.version = SCRIPT_VERSION
args = my_parser.parse_args()

USERNAME: str = args.username
FILE_NAME: str = args.file

# if arguments are not provided exit
if not USERNAME or not FILE_NAME:
    print("Missing arguments - username or file name")
    sys.exit()

# read file and store devices
if not os.path.isfile(FILE_NAME):
    print(f"File {FILE_NAME} was not found")
    sys.exit()

with open(FILE_NAME, "r", encoding='utf8') as f:
    device_names: list = f.read().splitlines()

# print devices from the file
print(f'{"Device Name": <30}{"Action":>10}')
print(SEPARATOR)

for device_name in device_names:
    print(f'{device_name:<30}{"Delete":>10}')


# promp user for password
print(SEPARATOR)
password: str = getpass.getpass(prompt=f'Enter Password for {USERNAME}: ', stream=None)
print(SEPARATOR)

# instantiate ISE API
api = IdentityServicesEngineAPI(username=USERNAME,
                                password=password,
                                uses_api_gateway=True,
                                base_url=BASE_URL,
                                version='3.0.0',
                                verify=False)

# try to login and execute command to ISE, if not successful end script
try:
    _ = api.network_device.get_network_device().response
    print(SEPARATOR, "Connection to ISE successful", SEPARATOR, sep="\n")
except ApiError:
    print(SEPARATOR, "Connection to ISE not successful, try again", SEPARATOR, sep="\n")
    sys.exit()


# delete devices
def delete_ise_device(name: str) -> bool:
    """
    return: True if device deleted, False if not found or other API error
    """
    try:
        _ = api.network_device.delete_by_name(name)
        return True
    except ApiError:
        return False


confirm = input(f"Delete {len(device_names)} devices ? [n]/y: ")

if confirm.lower() != "y":
    print("Invalid option selected")
    sys.exit()

print(SEPARATOR)
print(f'{"Device Name": <30}{"Status":>10}')
print(SEPARATOR)

for device in device_names:
    if delete_ise_device(device):
        print(f'{device:<30}{"Deleted":>10}')
    else:
        print(f'{device:<30}{"Not found":>10}')

print(SEPARATOR)
print(f"Script finished {datetime.now().strftime('%d%b%Y-%H%M%S')}")
print(SEPARATOR)

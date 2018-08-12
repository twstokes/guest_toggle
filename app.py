"""Toggles an interface on an Asus Router running Asuswrt-Merlin"""

from os import environ
from subprocess import PIPE, run
from flask import Flask

app = Flask(__name__)

USER = environ.get('ROUTER_USER')
HOSTNAME = environ.get('ROUTER_HOSTNAME')
INTERFACE = environ.get('ROUTER_INTERFACE')

SSH_COMMAND = ["ssh", "{}@{}".format(USER, HOSTNAME)]
BASE_COMMAND = SSH_COMMAND + ["ifconfig {}".format(INTERFACE)]
STATUS_COMMAND = SSH_COMMAND + ["cat /sys/class/net/{}/flags".format(INTERFACE)]

@app.route("/state")
def state():
    """Return whether the interface is enabled or disabled"""
    process = run(STATUS_COMMAND, stdout=PIPE)
    status_code = process.stdout.decode('utf-8').strip()

    if status_code == '0x1303':
        return "ENABLED"

    if status_code == '0x1302':
        return "DISABLED"

    return "UNEXPECTED STATUS CODE: {}".format(status_code)

@app.route("/disable")
def disable():
    """Disable the interface"""
    process = run(BASE_COMMAND + ["down"])
    return process_return_code(process.returncode)

@app.route("/enable")
def enable():
    """Enable the interface"""
    process = run(BASE_COMMAND + ["up"])
    return process_return_code(process.returncode)

def process_return_code(code):
    """Returns whether the process was a success or not"""
    if code == 0:
        return "SUCCESS"

    return "FAILURE: {}".format(code)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

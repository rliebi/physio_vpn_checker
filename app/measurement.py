import subprocess
import time
import pickle
from notifier import pusher
from settings import PAUSE_WHEN_RESTARTING_L2TP

__author__ = 'remoliebi'


def restart_ipsec():
    command = ['/usr/sbin/service', 'ipsec', 'restart']
    # shell=FALSE for sudo to work.
    try:
        subprocess.call(command, shell=False)
        time.sleep(PAUSE_WHEN_RESTARTING_L2TP)
    except OSError as e:
        pusher.push("failed to restart ipsec service", str(e))


def ipsec_status():
    p = subprocess.Popen(['program', 'arg1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    pusher.push('IPSec Status', output)
    pusher.log(output)

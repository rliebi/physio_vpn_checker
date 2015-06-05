import subprocess
import time

from notifier import pusher
from settings import PAUSE_WHEN_RESTARTING_L2TP, DEBUG


__author__ = 'remoliebi'


def restart_ipsec():
    if DEBUG:
        command = ['echo', 'would be restarting ipsec now but I am in DEBUG mode']
    else:
        command = ['/usr/sbin/service', 'ipsec', 'restart']

    # shell=FALSE for sudo to work.
    try:
        subprocess.call(command, shell=False)
        time.sleep(PAUSE_WHEN_RESTARTING_L2TP)
    except OSError as e:
        pusher.push("failed to restart ipsec service", str(e))


def ipsec_status():
    try:
        p = subprocess.Popen(['/usr/sbin/service', 'ipsec', 'status'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    except OSError as e:
        output = str(e)
    pusher.push('IPSec Status', output)
    pusher.log(output)



from checker import settings
from checker.notifier import Notifier
pusher = Notifier()

from checker.measurement import restart_ipsec, ipsec_status

from location import Location

__author__ = 'remoliebi'

import time

locations = [Location('basel', '192.168.81.1')]
all_down = False
while True:
    down_connections = []
    for l in locations:
        if not l.check_connection():
            down_connections.append(l)

    if len(down_connections) == len(locations):
        if not all_down:
            pusher.push('ALL Connections are down!', 'trying to restart the l2tp service', 2)
            restart_ipsec()

        if all_down:
            ipsec_status()
        all_down = True

    elif all_down:
        all_down = False
        pusher.push('Back to normal.',
                    ','.join([i.get_connection_phrase() for i in locations]))

    time.sleep(2)  # sleep 10 seconds
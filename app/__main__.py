# -*- coding: UTF-8 -*-

import re
import subprocess
import time
import sys

from location import Location
from measurement import ipsec_status, restart_ipsec
from notifier import pusher
from settings import PROWL_NOTIFY_API_KEYS, CHECK_INTERVAL


def check_settings():
    try:
        assert len(PROWL_NOTIFY_API_KEYS) > 0, "NO PROWL_NOTIFY_API_KEYS is set."
        return True
    except AssertionError as e:
        print e.message


def check_all_locations(locations):
    try:
        ips = [l.ip for l in locations]
        p = subprocess.Popen(['fping'] + ips, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        return output
    except OSError as e:
        pusher.push('Check All Locations', str(e))


def main():
    __author__ = 'remoliebi'
    status_regex = re.compile("(\d+\.\d+\.\d+\.\d+).*?(alive|unreachable)")
    locations = [
        Location('Basel', '192.168.81.1', 'basel@physio-zentrum.ch'),
        Location('St.Gallen', '192.168.129.1', 'stgallen@physio-zentrum.ch'),
        Location('Wetzikon', '172.16.6.1', 'wetzikon@physio-zentrum.ch'),
        Location('Server', '192.168.70.5', 'remo@liebi.net')
    ]
    restarted = False
    downtime_counter = 0
    while True:
        down_connections = []
        result = status_regex.findall(check_all_locations(locations))
        for i in range(len(result)):
            ip = result[i][0]
            reply = result[i][1]
            location = (item for item in locations if item.ip == ip).next()
            if reply == 'unreachable':
                down_connections.append(location)
                location.check_location(False)
            else:
                location.check_location(True)

        if len(down_connections) >= 3:
            downtime_counter += 1

            if not restarted and downtime_counter == 4:
                message = """ Hallo. <p>Es gab ein Problem mit den Verbindungen mit mehreren Standorten</p>
                <p>({down})</p>
                Der Server wird nun automatisch neu gestartet.
                Dies kann dazu führen, dass Simed kurzzeitig unterbrochen wird.

                Sorry für die umstände.<br/><br/>
                Lieber Gruss
                Remo
                <br/><br/><br/>
                ===<br/>
                {locations}
                """.format(locations='<br/>'.join([i.get_connection_phrase() for i in locations]),
                           down=','.join([i.name for i in down_connections]))

                pusher.send_mail(locations, "Neustart", message)
                pusher.push('trying to restart the l2tp service in 60 seconds',
                            '{} Connections are down!({})'.format(len(down_connections),
                                                                  ', '.join([i.name for i in down_connections])),
                            2)

                ipsec_status()
                time.sleep(60)
                restart_ipsec()
                restarted = True

            if restarted and downtime_counter % 6 == 0:
                ipsec_status()

        elif restarted:
            restarted = False
            pusher.push('IPSec seems to be running again.',
                        ','.join([i.get_connection_phrase() for i in locations]))
            downtime_counter = 0
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        if check_settings():
            main()
        else:
            print 'failed loading settings. please check your vpn_checker.conf' \
                  ' and settings.py or that the env variables are set correctly!'
    else:
        for arg in sys.argv:
            if arg == '__main__.py':
                pass

            if arg == 'testmail':
                l = Location('testlocation', '', 'remo@liebi.net')
                pusher.send_mail(l, 'TestMail', 'TestMail')
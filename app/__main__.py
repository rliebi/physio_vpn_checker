import re
import subprocess
import time

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
        Location('Basel', '192.168.81.1'),
        Location('Basel_TEST', '192.168.81.2'),
        Location('Basel_TEST1', '192.168.81.3'),
        Location('Basel_TEST2', '192.168.81.4'),
        Location('St.Gallen', '192.168.129.1'),
        Location('Wetzikon', '172.16.6.1'),
        Location('Server', '192.168.70.5')
    ]
    restarted = False
    downtime_counter = 0
    while True:
        down_connections = []
        result = status_regex.findall(check_all_locations(locations))
        for i in range(len(result)):
            if result[i][1] == 'unreachable':
                down_connections.append(locations[i])
                locations[i].check_location(False)
            else:
                locations[i].check_location(True)
            pusher.log(locations[i].get_connection_phrase())

        if len(down_connections) >= 3:
            downtime_counter += 1

            if not restarted and downtime_counter == 4:
                pusher.push('trying to restart the l2tp service',
                            '{} Connections are down!({})'.format(len(down_connections),
                                                                  ', '.join([i.name for i in down_connections])),
                            2)
                ipsec_status()
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
    if check_settings():
        main()
    else:
        print 'failed loading settings. please check your vpn_checker.conf' \
              ' and settings.py or that the env variables are set correctly!'
from location import Location
from measurement import restart_ipsec, ipsec_status
from notifier import pusher
from settings import CHECK_INTERVAL


def main():



    __author__ = 'remoliebi'

    import time

    locations = [Location('basel', '192.168.81.1'), Location('stgallen', '192.168.129.1'),
                 Location('wetzikon', '172.16.6.1'), Location('test', '192.168.66.54')]
    all_down = False
    while True:
        down_connections = []
        for l in locations:
            if not l.check_connection():
                down_connections.append(l)
            print l.get_connection_phrase()

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

        time.sleep(CHECK_INTERVAL)  # sleep 10 seconds


if __name__ == '__main__':
    main()
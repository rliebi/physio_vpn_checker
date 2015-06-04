from location import Location
from measurement import restart_ipsec, ipsec_status
from notifier import pusher
from settings import CHECK_INTERVAL


def main():
    __author__ = 'remoliebi'

    import time

    locations = [Location('Basel', '192.168.81.1'), Location('St.Gallen', '192.168.129.1'),
                 Location('Wetzikon', '172.16.6.1'), Location('Server', '192.168.70.5')]
    all_down = False
    while True:
        down_connections = []
        for l in locations:
            if not l.check_connection():
                down_connections.append(l)
            print l.get_connection_phrase()

        if len(down_connections) >= 2:
            if not all_down:
                pusher.push('trying to restart the l2tp service',
                            '{} Connections are down!({})'.format(len(down_connections),
                                                                  ', '.join([i.name for i in down_connections])),
                            2)
                restart_ipsec()

            if all_down:
                ipsec_status()
            all_down = True

        elif all_down:
            all_down = False
            pusher.push('Back to normal.',
                        ','.join([i.get_connection_phrase() for i in locations]))

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
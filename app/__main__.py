from location import Location
from measurement import restart_ipsec, ipsec_status
from notifier import pusher
from settings import CHECK_INTERVAL, PROWL_NOTIFY_API_KEYS


def check_settings():
    try:
        assert len(PROWL_NOTIFY_API_KEYS) > 0, "NO PROWL_NOTIFY_API_KEYS is set."
        return True
    except AssertionError as e:
        print e.message


def main():
    __author__ = 'remoliebi'

    import time

    locations = [Location('Basel', '192.168.81.1'), Location('St.Gallen', '192.168.129.1'),
                 Location('Wetzikon', '172.16.6.1'), Location('Server', '192.168.70.5')]
    restarted = False
    downtime_counter = 0
    while True:
        down_connections = []
        for l in locations:
            if not l.check_connection():
                down_connections.append(l)

        if len(down_connections) >= 2:
            downtime_counter += 1

            if not restarted and downtime_counter == 4:
                pusher.push('trying to restart the l2tp service',
                            '{} Connections are down!({})'.format(len(down_connections),
                                                                  ', '.join([i.name for i in down_connections])),
                            2)
                ipsec_status()
                restart_ipsec()

            if restarted:
                ipsec_status()
            restarted = True

        elif restarted:
            restarted = False
            pusher.push('Back to normal.',
                        ','.join([i.get_connection_phrase() for i in locations]))

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    if check_settings():
        main()
    else:
        print 'failed loading settings. please check your vpn_checker.conf' \
              ' and settings.py or that the env variables are set correctly!'
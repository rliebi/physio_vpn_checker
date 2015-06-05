from measurement import restart_ipsec
from notifier import pusher

__author__ = 'remoliebi'
import os

import settings


class Location:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.timeout_counter = 0
        self.connected = False

    def check_connection(self):
        # test the connection. use network manager in near future
        self.connected = os.system('fping -c 1 -t 1000 %s 2&>1' % self.ip) == 0
        if self.connected:
            if self.timeout_counter > settings.SEND_NOTIFICATION_AFTER:
                pusher.push("{} is up and running".format(self.name), 'All back to normal')
                self.timeout_counter = 0
            return True
        else:
            pusher.log('{} is down.'.format(self.name))
            self.raise_counter()
            return False

    def raise_counter(self):
        self.timeout_counter += 1
        if (self.timeout_counter % settings.SEND_NOTIFICATION_EVERY == 0
                and self.timeout_counter >= settings.SEND_NOTIFICATION_AFTER)\
                or self.timeout_counter == settings.SEND_NOTIFICATION_AFTER:
            pusher.push('{} not connected'.format(self.name),
                        'this was the {}. attempt'.format(self.timeout_counter))
        if self.timeout_counter == settings.NOTIFY_LOCATION_AFTER:
            pass  # send email

        if self.timeout_counter == settings.RESTART_L2TP_AFTER:
            restart_ipsec()

    def get_connection_phrase(self):
        return "{} is {}".format(self.name, 'up' if self.connected else 'down')
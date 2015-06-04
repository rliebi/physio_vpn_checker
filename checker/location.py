from checker import pusher
from checker.measurement import restart_ipsec

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
        self.connected = os.system('ping -c 1 %s' % self.ip) == 0
        if self.connected:
            if self.timeout_counter > 0:
                pusher.push("{} is up and running".format(self.name), 'All back to normal')
                self.timeout_counter = 0
            return True
        else:
            self.raise_counter()
            return False

    def raise_counter(self):
        self.timeout_counter += 1
        if (self.timeout_counter % settings.SEND_NOTIFICATION_EVERY == 0
                and self.timeout_counter >= settings.SEND_NOTIFICATION_AFTER)\
                or self.timeout_counter == settings.SEND_NOTIFICATION_AFTER:
            pusher.push('{} not connected'.format(self.name),
                        'this was the {}. attempt'.format(self.timeout_counter))
        if self.timeout_counter == 10:
            pass  # send email

        if self.timeout_counter == settings.RESTART_L2TP_AFTER:
            restart_ipsec()

    def get_connection_phrase(self):
        return "{} is {}".format(self.name, 'up' if self.connected else 'down')
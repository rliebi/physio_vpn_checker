from measurement import restart_ipsec
from notifier import pusher

__author__ = 'remoliebi'

import settings


class Location:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.timeout_counter = 0
        self.stability_index = 100
        self.is_connected = False
        self.notified = 0

    def check_location(self, connection_status):
        if connection_status:
            self.connected()
            if self.stability_index < 100 and self.stability_index % settings.SEND_NOTIFICATION_EVERY == 0:
                pusher.push('{} stability is rising'.format(self.name),
                            '{} SI: {}'.format(self.get_connection_phrase(), self.stability_index))

            if self.notified > 0 and self.stability_index == 100:
                self.notified = 0
                pusher.push('{} is stable'.format(self.name),
                            '{} SI: {}'.format(self.get_connection_phrase(), self.stability_index))

        else:
            self.disconnected()
            if self.stability_index < 100 and self.timeout_counter + self.stability_index < 100:
                if self.stability_index + self.notified < (100 - settings.SEND_NOTIFICATION_EVERY):
                    self.notified += settings.SEND_NOTIFICATION_EVERY
                    pusher.push('{} stability is low'.format(self.name),
                                '{} SI: {}'.format(self.get_connection_phrase(), self.stability_index))

    def connected(self):
        self.is_connected = True
        self.timeout_counter = 0
        self.stability_index += 1 if self.stability_index < 100 else 0

    def disconnected(self):
        self.is_connected = False
        self.stability_index -= 1 if self.stability_index >= 0 else 0
        self.timeout_counter += 1
        pusher.log(self.get_connection_phrase())
        if self.timeout_counter % settings.SEND_NOTIFICATION_EVERY == 0 \
                and self.timeout_counter >= settings.SEND_NOTIFICATION_AFTER:
            pusher.push('{} not connected'.format(self.name),
                        'this was the {}. attempt. Stability Index: {}'.format(self.timeout_counter,
                                                                               self.stability_index))
        if self.timeout_counter == settings.NOTIFY_LOCATION_AFTER:
            pass  # send email

        if self.timeout_counter == settings.RESTART_L2TP_AFTER:
            restart_ipsec()

    def get_connection_phrase(self):
        return "{} is {}".format(self.name, 'up' if self.is_connected else 'down')
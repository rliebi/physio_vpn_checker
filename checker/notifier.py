from checker import settings

__author__ = 'remoliebi'

import pyrowl


class Notifier:
    def __init__(self):
        self.p = pyrowl.Pyrowl(settings.PROWL_NOTIFY_API_KEYS)

    def push(self, event, description, priority=0):
        print 'sending notification'
        print self.p.push("PHYSIOZENTRUM", event, description, '', priority)
import pyrowl
from settings import PROWL_NOTIFY_API_KEYS

__author__ = 'remoliebi'


class Notifier:
    def __init__(self):
        self.p = pyrowl.Pyrowl(PROWL_NOTIFY_API_KEYS)

    def push(self, event, description, priority=0):
        print 'sending notification'
        print self.p.push("PHYSIOZENTRUM", event, description, '', priority)


pusher = Notifier()
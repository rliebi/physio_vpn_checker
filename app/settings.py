import os

__author__ = 'remoliebi'

def get_multiple_env_args(name):
    counter = 0
    while True:
        counter += 1
        key = os.environ.get(name + str(counter))
        if key is None:
            break
        yield key

CHECK_INTERVAL = 10  # in seconds
PAUSE_WHEN_RESTARTING_L2TP = 20  # in seconds
SEND_NOTIFICATION_AFTER = 5  # in retries
SEND_NOTIFICATION_EVERY = 10  # in retries
NOTIFY_LOCATION_AFTER = 10  # in retries
RESTART_L2TP_AFTER = 30  # if a single location fails, i will restart the l2tp server after xx retries
PROWL_NOTIFY_API_KEYS = [value for value in get_multiple_env_args('PROWL_API_KEY')]
print 'API KEYS', PROWL_NOTIFY_API_KEYS
SMTP_PASS = os.environ.get('SMTP_PASS')
SMTP_HOST = 'plesk.liebi.net'
SMTP_USER = 'noreply@lnh.ch'

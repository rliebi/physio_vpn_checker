import smtplib
import datetime

import pyrowl
from settings import PROWL_NOTIFY_API_KEYS, SMTP_HOST, SMTP_PASS, SMTP_USER


__author__ = 'remoliebi'


class Notifier:
    def __init__(self):
        self.p = pyrowl.Pyrowl(PROWL_NOTIFY_API_KEYS)
        self.smtpObj = smtplib.SMTP_SSL(SMTP_HOST, 465)

    def push(self, event, description, priority=0, url=''):
        self.p.push("PHYSIOZENTRUM", event, description, url, priority)
        self.log('{} - {}'.format(event, description))

    def log(self, output):
        print '{time} - {log}'.format(time=datetime.datetime.now(), log=output)

    def send_mail(self, location, event, description, url):
        location_mail = location + '@physio-zentrum.ch'
        sender = 'noreply@lnh.ch'
        receivers = ['remo@liebi.net']

        message = """From: Remo Liebi <noreply@liebi.biz>
        To: {rcp_name} <{rcp_email}>
        Subject: {event}

        {description}

        {url}
        """.format(rcp_name=location, rcp_email=location_mail, description=description, url=url, event=event)

        try:
            print SMTP_USER, SMTP_PASS, SMTP_HOST
            print self.smtpObj.login(SMTP_USER, SMTP_PASS)
            self.smtpObj.sendmail(sender, receivers, message)
            print "Successfully sent email"
        except smtplib.SMTPException:
            raise
            print "Error: unable to send email"


pusher = Notifier()
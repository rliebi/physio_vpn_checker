import smtplib
import datetime
import sendgrid
import pyrowl
from settings import PROWL_NOTIFY_API_KEYS, SMTP_HOST, SMTP_PASS, SMTP_USER, PROWL_APP_NAME, SENDGRID_API_KEY


__author__ = 'remoliebi'


class Notifier:
    def __init__(self):
        self.p = pyrowl.Pyrowl(PROWL_NOTIFY_API_KEYS)
        self.smtpObj = smtplib.SMTP_SSL(SMTP_HOST, 465)

        self.sg = sendgrid.SendGridClient(SENDGRID_API_KEY)

    def push(self, event, description, priority=0, url=''):
        self.p.push(PROWL_APP_NAME, event, description, url, priority)
        self.log('{} - {}'.format(event, description))

    def log(self, output):
        print '{time} - {log}'.format(time=datetime.datetime.now(), log=output)

    def send_mail(self, location, event, description):
        from location import Location

        if isinstance(location, Location):
            location = [location]
        message = sendgrid.Mail()
        for l in location:
            message.add_to(l.email)
            print l.email
        message.add_to("clandolt@physio-zentrum.ch")
        message.add_to("remo@liebi.net")
        message.set_from("remo@liebi.net")
        message.set_subject(event)
        message.set_html(description)
        self.sg.send(message)


pusher = Notifier()
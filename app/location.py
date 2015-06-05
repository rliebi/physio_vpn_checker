# -*- coding: UTF-8 -*-
from measurement import restart_ipsec
from notifier import pusher

__author__ = 'remoliebi'

import settings


class Location:
    def __init__(self, name, ip, email=None):
        self.name = name
        self.ip = ip
        self.timeout_counter = 0
        self.stability_index = 100
        self.is_connected = False
        self.notified = 0
        self.email = email or name + "@physio-zentrum.ch"
        self.stability_mail_sent = False

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
            if self.stability_index < 100 and self.timeout_counter + self.stability_index < 100 \
                    and self.stability_index % settings.SEND_NOTIFICATION_EVERY == 0:
                if self.stability_index + self.notified < (100 - settings.SEND_NOTIFICATION_EVERY):
                    self.notified += settings.SEND_NOTIFICATION_EVERY
                    pusher.push('{} stability is low'.format(self.name),
                                '{} SI: {}'.format(self.get_connection_phrase(), self.stability_index))
                    if not self.stability_mail_sent:
                        self.stability_mail_sent = True
                        pusher.send_mail(self, 'Verbindungsstabilität', """
                        Hallo Team {team}<br/>
                                 <p>Es gab ein Problem mit der Verbindung mit dem Rechenzentrum.
                                 Die Verbindung ist sehr instabil.</p>

                                 <p>Der Stabilitätsindex ist {index}/100</p>
                                <p>Dadurch kann es zu kurzen unterbrüchen von Simed kommen.</p>
                                 <p>Um das Problem zu beheben soll folgendermassen vorgegangen werden:
                                 <ul>
                                 <li>Schaltet alle Geräte im Server-Schrank aus. (<strong>Achtung</strong> Die
                                 Telefonverbindung geht durch das ebenfalls verloren)</li>
                                 <li>Wartet 30 Sekunden</li>
                                 <li>Schaltet die Geräte wieder ein.</li>
                                 <li>nach ca. 2 Minuten sollte die Simed Verbindung wieder funktionieren</li>
                                </ul></p>
                                <p>
                                Lieber Gruss<br/>
                                Remo
                                </p>
                        """.format(index=self.stability_index, team=self.name))


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
            pusher.send_mail(self, 'Die Verbindung mit dem Rechenzentrum ging verloren.',
                             """
                             Hallo Team {team}<br/>
                             <p>Es gab ein Problem mit der Verbindung mit dem Rechenzentrum.
                             Simed ist nicht verfügbar.</p>

                             <p>Die Verbindung ist seit ca. {} Minuten ausgefallen.</p>

                            <p> Um das Problem zu beheben soll folgendermassen vorgegangen werden:
                             <ul>
                             <li>Schaltet alle Geräte im Server-Schrank aus. (<strong>Achtung</strong> Die
                             Telefonverbindung geht durch das ebenfalls verloren)</li>
                             <li>Wartet 30 Sekunden</li>
                             <li>Schaltet die Geräte wieder ein.</li>
                             <li>nach ca. 2 Minuten sollte die Simed Verbindung wieder funktionieren</li>
                            </ul></p>
                             <p>Sollte dies nicht der Fall sein:
                             Bitte benutzt die direkte VPN Verbindung am iMac um eine Notfall-Verbindung aufzubauen.
                            </p>
                            <p>
                            Ich weiss bereits über das Problem bescheid und kümmere mich schnellst möglich um eine Lösung.
                            </p>
                            <p>
                            Lieber Gruss<br/>
                            Remo
                            </p>

                             """.format(self.timeout_counter * settings.CHECK_INTERVAL / 60, team=self.name))
            pass  # send email

        if self.timeout_counter == settings.RESTART_L2TP_AFTER:
            restart_ipsec()

    def get_connection_phrase(self):
        return "{} is {}".format(self.name, 'up' if self.is_connected else 'down')
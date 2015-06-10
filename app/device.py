import re
from urllib2 import urlopen, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener

__author__ = 'remoliebi'


class Device:
    def __init__(self, username, password, ip, type=None):
        self.username = username
        self.password = password
        self.ip = ip
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        handler = HTTPBasicAuthHandler(password_mgr)
        password_mgr.add_password(None, self.ip, self.username, self.password)
        self.opener = build_opener(handler)
        pass

    def check(self):

        address = self.ip + '/userRpm/Monitor_sysinfo.htm'
        res = self.opener.open(address)
        pageData = res.read()
        p = re.compile('(?<=line1=)(.*)(?=;)')
        parsed = p.findall(pageData)
        print parsed
        # print pageData
        print address
        # response = urlopen(self.ip)
        # html = response.read()
        # print html

    def reboot(self):
        address = self.ip + '/userRpm/SysRebootRpm.htm?Reboot=Reboot'
        try:
            self.opener.open(address)
            return True
        except:
            return False
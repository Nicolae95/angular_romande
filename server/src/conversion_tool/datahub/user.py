# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import pytz
import os
import uuid
import requests
from collections import defaultdict
from operator import itemgetter

api = 'http://energymarketprice.com/WebServices'


class User():
    user = {}
    token = ''

    def __init__(self):
        self.user['UserName'] = 'usr33485'
        self.user['Password'] = 'c0ffd810'

    def login(self):
        headers = {'content-type': 'application/json'}
        response = requests.post(api + '/Account', data=json.dumps(self.user), headers=headers)
        try:
            self.token = json.loads(response.content)['Authorization']
            print 'token login'
            wtfile = open("datahub/token.txt", "r+")
            print 'wtfile', wtfile
            wtfile.truncate()
            wtfile.write(self.token)
            wtfile.close()
        except:
            self.token = ''

    def get_token_file(self):
        tfile = open("datahub/token.txt", "r")
        print 'token from file'
        self.token = tfile.read()

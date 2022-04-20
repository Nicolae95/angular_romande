# -*- coding: utf-8 -*-
import json
import requests
import csv
from datetime import datetime, timedelta
import re

r = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/standard?op=LISTSTATUS')
print r
json_data = json.loads(r.text)
pfcs = json_data['FileStatuses']['FileStatus']
last = pfcs[-1]
print 'last = ', last


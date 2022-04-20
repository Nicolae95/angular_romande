# -*- coding: utf-8 -*-
import json
import requests
import csv
from datetime import datetime, timedelta
import re

api = "https://s1empprddb.pegase.lan/api/pfc/upload-api/"
try:
    r = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/standard?op=LISTSTATUS')
    json_data = json.loads(r.text)
    pfcs = json_data['FileStatuses']['FileStatus']
    last = pfcs[-1]
    print 'last = ', last
except:
    last = {}

csv_address = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/standard/'
csv_risq = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/primes_risque_kwh_RMM/standard/primes_risque_csv/'
csv_eco = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/prix_kwh_AGE/standard/prix_garanties_origine_kwh_csv/'

obj = {}
today = datetime.now().strftime("%Y%m%d")
address = last['pathSuffix']
file_date = last['pathSuffix'][10:18]
file_hour = last['pathSuffix'][18:22]
csv_path = csv_address + address + '?op=OPEN'

print 'csv = ', csv_path, file_date, file_hour
print today, file_date, today == file_date

risq = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/primes_risque_kwh_RMM/standard/primes_risque_csv?op=LISTSTATUS')
risq_jaon = json.loads(risq.text)
risq_addr = risq_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
rdata = requests.get(csv_risq + risq_addr + '?op=OPEN').text
rlines = rdata.splitlines()
obj['risqs'] = [line.split(';') for line in rlines]


ecos = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/prix_kwh_AGE/standard/prix_garanties_origine_kwh_csv?op=LISTSTATUS')
ecos_jaon = json.loads(ecos.text)
eco_addr = ecos_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
edata = requests.get(csv_eco + eco_addr + '?op=OPEN').text
elines = edata.splitlines()
obj['eco'] = [line.split(';') for line in elines]

data = requests.get(csv_path).text
lines = data.splitlines()
obj['pfc'] = [line.split(';') for line in lines]
obj['path'] = address
obj['risc_file'] = risq_addr
obj['eco_file'] = eco_addr
dat_str = datetime.strptime(file_date, '%Y%m%d')
dat = dat_str.strftime('%d.%m.%Y')
obj['obj'] = dat
obj['hour'] = file_hour[:2] + ':' + file_hour[2:]
headers = {'content-type': 'application/json'}
print obj['obj'], 
response = requests.post(api, data=json.dumps(obj), headers=headers, verify='/home/romande/tasks/prod/s1empprddb.pegase.lan.pem')
print response

print 'object === ', obj['obj']
print 'object hour === ', obj['hour']

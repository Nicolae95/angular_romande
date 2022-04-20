# -*- coding: utf-8 -*-
import json
import requests
import csv
from datetime import datetime, timedelta
import re
from collections import defaultdict

try:
    opr = requests.get('https://s1empprddb.pegase.lan/api/pfc/opportunites/' , verify='/home/romande/tasks/prod/s1empprddb.pegase.lan.pem')
    print 'opr', opr.text
    json_data = json.loads(opr.text)
    opportunites = json_data['nr_opportunites']
    print 'opportunites = ', opportunites
except:
    opportunites = []

api = "https://s1empprddb.pegase.lan/api/pfc/upload-sme/"

offers = defaultdict()
for opportunity, oid in opportunites:
    try:
        r = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/sur_mesure/' + opportunity + '-' + str(oid) + '?op=LISTSTATUS')
        json_data = json.loads(r.text)
        pfcs = json_data['FileStatuses']['FileStatus']
        last = pfcs[-1]
        print 'last = ', last
    except:
        last = {}

    csv_address = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/sur_mesure/'+ opportunity + '-' + str(oid) + '/'
    csv_risq = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/primes_risque_kwh_RMM/sur_mesure/' + opportunity + '-' + str(oid) + '/primes_risque_csv/'
    csv_eco = 'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/prix_kwh_AGE/sur_mesure/' + opportunity + '-' + str(oid) + '/prix_garanties_origine_kwh_csv/'

    obj = {}
    today = datetime.now().strftime("%Y%m%d")
    try:
        address = last['pathSuffix']
        file_date = last['pathSuffix'][10:18]
        file_hour = last['pathSuffix'][18:22]
    except:
        address = ''
        file_date = ''
        file_hour = ''
    
    csv_path = csv_address + address + '?op=OPEN'

    print 'csv = ', csv_path, file_date, file_hour
    print today, file_date, today == file_date

    risq = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/primes_risque_kwh_RMM/sur_mesure/' +
                        opportunity + '-' + str(oid) + '/primes_risque_csv?op=LISTSTATUS')
    risq_jaon = json.loads(risq.text)
    
    try:
        risq_addr = risq_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
        rdata = requests.get(csv_risq + risq_addr + '?op=OPEN').text
        rlines = rdata.splitlines()
        obj['risqs'] = [line.split(';') for line in rlines]
        print('risqs = ', csv_risq + risq_addr + '?op=OPEN')
        print('risqs = ', obj['risqs'])
    except:
        obj['risqs'] = []
        risq_addr = ''

    ecos = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/prix_kwh_AGE/sur_mesure/' +
                        opportunity + '-' + str(oid) + '/prix_garanties_origine_kwh_csv?op=LISTSTATUS')
    ecos_jaon = json.loads(ecos.text)
    try:
        eco_addr = ecos_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
        edata = requests.get(csv_eco + eco_addr + '?op=OPEN').text
        elines = edata.splitlines()
        obj['eco'] = [line.split(';') for line in elines]
        print('eco = ', csv_eco + eco_addr + '?op=OPEN')
        print('eco = ', obj['eco'])
    except:
        obj['eco'] = []
        eco_addr = ''

    try:
        data = requests.get(csv_path).text
        lines = data.splitlines()
        obj['pfc'] = [line.split(';') for line in lines]
    except:
        obj['pfc'] = []
    obj['path'] = address
    obj['risc_file'] = risq_addr
    obj['eco_file'] = eco_addr
    try:
        dat_str = datetime.strptime(file_date, '%Y%m%d')
        dat = dat_str.strftime('%d.%m.%Y')
    except:
        dat = datetime.now().strftime('%d.%m.%Y')
    obj['hour'] = file_hour[:2] + ':' + file_hour[2:]
    obj['obj'] = dat + ' ' + file_hour[:2] + ':' + file_hour[2:]
    obj['oid'] = oid
    offers[str(opportunity)] = obj


headers = {'content-type': 'application/json'}
response = requests.post(api, data=json.dumps({'offers': offers}), headers=headers, verify='/home/romande/tasks/prod/s1empprddb.pegase.lan.pem')
print response

# print 'object === ', offers
# print 'object hour === ', offers


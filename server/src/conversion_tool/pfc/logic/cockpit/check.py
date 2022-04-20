import json
import requests
import csv
from datetime import datetime, timedelta
import re
import pytz
import os
import time
from contextlib import closing
from collections import defaultdict
from operator import itemgetter
from pfc.models import *
from offers.models import *
from offers.serializers import *
from ..db.upload import upload_pfcnofile_market_db, upload_pfc_nofile_db


def new_data():
    print('get data')
    try:
        # r = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/standard?op=LISTSTATUS', timeout=2)
        r = requests.get('http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/PFC/Swiss/Ajustee_n5/standard?op=LISTSTATUS')
        json_data = json.loads(r.text)
        pfcs = json_data['FileStatuses']['FileStatus']
        last = pfcs[-1]
        print 'last = ', last
    except:
        last = {}
        return {}

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

    risq = requests.get(
        'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/primes_risque_kwh_RMM/standard/primes_risque_csv?op=LISTSTATUS')
    risq_jaon = json.loads(risq.text)
    risq_addr = risq_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
    print csv_risq + risq_addr + '?op=OPEN'
    rdata = requests.get(csv_risq + risq_addr + '?op=OPEN').text
    rlines = rdata.splitlines()
    obj['risqs'] = [line.split(';') for line in rlines]


    ecos = requests.get(
        'http://s1bigdataen.pegase.lan:50071/webhdfs/v1/metier/pricer/prix_kwh_AGE/standard/prix_garanties_origine_kwh_csv?op=LISTSTATUS')
    ecos_jaon = json.loads(ecos.text)
    eco_addr = ecos_jaon['FileStatuses']['FileStatus'][-1]['pathSuffix']
    print csv_eco + eco_addr + '?op=OPEN'
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
    print obj['obj']
    return obj



def update_data(pfc_data):
    print('update date to get last pfc data')
    risc = Risc.objects.get(name='Risque PwB')
    risc1 = Risc.objects.get(name__icontains='Risque volume')
    risc2 = Risc.objects.get(name='Risque prix')
    
    energy1, created3 = Risc.objects.get_or_create(code='energy1')
    energy2, created4 = Risc.objects.get_or_create(code='energy2')
    energy3, created5 = Risc.objects.get_or_create(code='energy3')
    energy4, created6 = Risc.objects.get_or_create(code='energy4')
    energy5, created7 = Risc.objects.get_or_create(code='energy5')
    energy6, created8 = Risc.objects.get_or_create(code='energy6')

    print('energy6 == ', energy6)
    # if PFC.objects.filter(pfc_id=request.data['obj'], time=' ' + request.data['hour']).exists():
    #     return Response({'received data': 'such pfc exists'}, status=status.HTTP_400_BAD_REQUEST)

    currentPfc = PFC.objects.filter(pfc_id=pfc_data['obj'])
    print('currentPfc == ', currentPfc)
    if currentPfc:
        if str(pfc_data['hour']).strip() != str(currentPfc[0].time).strip():
            currentPfc[0].pfc_id = currentPfc[0].pfc_id + ' ' + str(currentPfc[0].time)
            currentPfc[0].time = None
            currentPfc[0].save()
    
    # pfc, created = PFC.objects.get_or_create(pfc_id=pfc_data['obj'], time=' ' + pfc_data['hour'], file=pfc_data['path'],
    #                                         risc=pfc_data['risc_file'], eco=pfc_data['eco_file'])
    
    pfc, created = PFC.objects.get_or_create(pfc_id=pfc_data['obj'], time=' ' + pfc_data['hour'], file=pfc_data['path'])

    print('pfc == ', pfc, created)
    if created:
        print('pfc created')
        pfc.risc = pfc_data['risc_file']
        pfc.eco = pfc_data['eco_file']
        pfc.save()
        streampfc = StringIO.StringIO()
        writerpfc = csv.writer(streampfc, delimiter='\t')
        for index, obj in enumerate(pfc_data['pfc']):
            if index > 0:
                date = datetime.strptime(str(obj[0]), '%d.%m.%Y %H:%M')
                # print('pfc = ', [datetime.now(), datetime.now(), pfc.id, float(obj[2]), date, timedelta(hours=1), 'CHF'])
                writerpfc.writerow([datetime.now(), datetime.now(), pfc.id, float(obj[2]), date, timedelta(hours=1), 'CHF'])
        upload_pfc_nofile_db(streampfc)

        for index, risq in enumerate(pfc_data['risqs']):
            if index > 0:
                # print 'riqs = ', risq
                RiscRecord.objects.create(risc=risc, value=float(risq[1]), pfc=pfc, file=pfc_data['risc_file'],  year=int(risq[0]))
                RiscRecord.objects.create(risc=risc1, value=float(risq[2]), pfc=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
                RiscRecord.objects.create(risc=risc2, value=float(risq[3]), pfc=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
        
        for index1, ecoq in enumerate(pfc_data['eco']):
            if index1 > 0:
                # print 'riqs = ', ecoq
                RiscRecord.objects.create(risc=energy2, value=float(ecoq[1]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy1, value=float(ecoq[2]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy6, value=float(ecoq[3]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy3, value=float(ecoq[4]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy5, value=float(ecoq[5]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy4, value=float(ecoq[6]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
    else:
        if pfc.file != pfc_data['path']:
            pfc.file = pfc_data['path']
            pfc.save()
        print('pfc risc already exists', pfc_data['risc_file'], pfc.risc != pfc_data['risc_file'])
        if pfc.risc != pfc_data['risc_file']:
            pfc.risc = pfc_data['risc_file']
            pfc.save()
            RiscRecord.objects.filter(pfc=pfc, risc=risc).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=risc1).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=risc2).update(pfc=None, rid=str(pfc.pfc_id))
            for index2, risq in enumerate(pfc_data['risqs']):
                if index2 > 0:
                    # print 'risq = ', risq
                    RiscRecord.objects.create(risc=risc, value=float(risq[1]), pfc=pfc, file=pfc_data['risc_file'],  year=int(risq[0]))
                    RiscRecord.objects.create(risc=risc1, value=float(risq[2]), pfc=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
                    RiscRecord.objects.create(risc=risc2, value=float(risq[3]), pfc=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
        
        print('pfc eco already exists', pfc_data['eco_file'], pfc.eco != pfc_data['eco_file'])
        if pfc.eco != pfc_data['eco_file']:
            pfc.eco = pfc_data['eco_file']
            pfc.save()
            RiscRecord.objects.filter(pfc=pfc, risc=energy2).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=energy1).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=energy6).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=energy3).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=energy5).update(pfc=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc=pfc, risc=energy4).update(pfc=None, rid=str(pfc.pfc_id))
            for ind, ecoq in enumerate(pfc_data['eco']):
                if ind > 0:
                    # print 'ecoq = ', ecoq
                    RiscRecord.objects.create(risc=energy2, value=float(ecoq[1]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy1, value=float(ecoq[2]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy6, value=float(ecoq[3]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy3, value=float(ecoq[4]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy5, value=float(ecoq[5]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy4, value=float(ecoq[6]), pfc=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
    return pfc


def update_market_data(opportunite, pfc_data):
    print('update date to get last pfc market data')
    risc = Risc.objects.get(name='Risque PwB')
    risc1 = Risc.objects.get(name__icontains='Risque volume')
    risc2 = Risc.objects.get(name='Risque prix')
    
    energy1, created3 = Risc.objects.get_or_create(code='energy1')
    energy2, created4 = Risc.objects.get_or_create(code='energy2')
    energy3, created5 = Risc.objects.get_or_create(code='energy3')
    energy4, created6 = Risc.objects.get_or_create(code='energy4')
    energy5, created7 = Risc.objects.get_or_create(code='energy5')
    energy6, created8 = Risc.objects.get_or_create(code='energy6')
    energy7, created9 = Risc.objects.get_or_create(code='energy7')
    energy8, created10 = Risc.objects.get_or_create(code='energy8')
    energy9, created11 = Risc.objects.get_or_create(code='energy9')

    print('energy6 == ', energy6)
    # if PFC.objects.filter(pfc_id=request.data['obj'], time=' ' + request.data['hour']).exists():
    #     return Response({'received data': 'such pfc exists'}, status=status.HTTP_400_BAD_REQUEST)

    currentPfc = PFCMarket.objects.filter(pfc_id=pfc_data['obj'])
    print('currentPfc == ', currentPfc)
    if currentPfc:
        if str(pfc_data['hour']).strip() != str(currentPfc[0].time).strip():
            currentPfc[0].pfc_id = currentPfc[0].pfc_id + ' ' + str(currentPfc[0].time)
            currentPfc[0].time = None
            currentPfc[0].save()

    # pfc, created = PFC.objects.get_or_create(pfc_id=pfc_data['obj'], time=' ' + pfc_data['hour'], file=pfc_data['path'],
    #                                         risc=pfc_data['risc_file'], eco=pfc_data['eco_file'])
    pfc, created = PFCMarket.objects.get_or_create(pfc_id=pfc_data['obj'], time=' ' + pfc_data['hour'], file=pfc_data['path'],
                                                     opportunite=opportunite, offer=int(pfc_data['oid']), custom=pfc_data['eco'][0][9])
    
    print('pfc market == ', pfc, created)

    if created:
        print('pfc market created')
        pfc.risc = pfc_data['risc_file']
        pfc.eco = pfc_data['eco_file']
        pfc.save()
        streampfc = StringIO.StringIO()
        writerpfc = csv.writer(streampfc, delimiter='\t')
        for index, obj in enumerate(pfc_data['pfc']):
            if index > 0:
                date = datetime.strptime(str(obj[0]), '%d.%m.%Y %H:%M')
                # print('pfc = ', [datetime.now(), datetime.now(), pfc.id, float(obj[2]), date, timedelta(hours=1), 'CHF'])
                writerpfc.writerow([datetime.now(), datetime.now(), pfc.id, float(obj[2]), date, timedelta(hours=1), 'CHF'])
        upload_pfcnofile_market_db(streampfc)
        
        print(pfc_data['risqs'])
        for index, risq in enumerate(pfc_data['risqs']):
            if index > 0:
                print 'riqs = ', risq
                RiscRecord.objects.create(risc=risc, value=float(risq[1]), pfc_market=pfc, file=pfc_data['risc_file'],  year=int(risq[0]))
                RiscRecord.objects.create(risc=risc1, value=float(risq[2]), pfc_market=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
                RiscRecord.objects.create(risc=risc2, value=float(risq[3]), pfc_market=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
        
        for index1, ecoq in enumerate(pfc_data['eco']):
            if index1 > 0:
                print 'riqs = ', ecoq
                RiscRecord.objects.create(risc=energy2, value=float(ecoq[1]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy1, value=float(ecoq[2]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy6, value=float(ecoq[3]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy3, value=float(ecoq[4]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy5, value=float(ecoq[5]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                RiscRecord.objects.create(risc=energy4, value=float(ecoq[6]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                if ecoq[7]:
                    RiscRecord.objects.create(risc=energy7, value=float(ecoq[7]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                else:
                    RiscRecord.objects.create(risc=energy7, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                if ecoq[8]:
                    RiscRecord.objects.create(risc=energy8, value=float(ecoq[8]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                else:
                    RiscRecord.objects.create(risc=energy8, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                if ecoq[9]:
                    RiscRecord.objects.create(risc=energy9, value=float(ecoq[9]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                else:
                    RiscRecord.objects.create(risc=energy9, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    
    else:
        if pfc.file != pfc_data['path']:
            pfc.file = pfc_data['path']
            pfc.save()
        print('pfc market risc already exists', pfc_data['risc_file'], pfc.risc != pfc_data['risc_file'])
        if pfc.risc != pfc_data['risc_file']:
            pfc.risc = pfc_data['risc_file']
            pfc.save()
            RiscRecord.objects.filter(pfc_market=pfc, risc=risc).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=risc1).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=risc2).update(pfc_market=None, rid=str(pfc.pfc_id))
            for index2, risq in enumerate(pfc_data['risqs']):
                if index2 > 0:
                    # print 'risq = ', risq
                    RiscRecord.objects.create(risc=risc, value=float(risq[1]), pfc_market=pfc, file=pfc_data['risc_file'],  year=int(risq[0]))
                    RiscRecord.objects.create(risc=risc1, value=float(risq[2]), pfc_market=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
                    RiscRecord.objects.create(risc=risc2, value=float(risq[3]), pfc_market=pfc, file=pfc_data['risc_file'], year=int(risq[0]))
        
        print('pfc market eco already exists', pfc_data['eco_file'], pfc.eco != pfc_data['eco_file'])
        if pfc.eco != pfc_data['eco_file']:
            pfc.eco = pfc_data['eco_file']
            pfc.custom = pfc_data['eco'][0][9]
            pfc.save()
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy2).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy1).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy6).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy3).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy5).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy4).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy7).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy8).update(pfc_market=None, rid=str(pfc.pfc_id))
            RiscRecord.objects.filter(pfc_market=pfc, risc=energy9).update(pfc_market=None, rid=str(pfc.pfc_id))
            for ind, ecoq in enumerate(pfc_data['eco']):
                if ind > 0:
                    # print 'ecoq = ', ecoq
                    RiscRecord.objects.create(risc=energy2, value=float(ecoq[1]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy1, value=float(ecoq[2]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy6, value=float(ecoq[3]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy3, value=float(ecoq[4]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy5, value=float(ecoq[5]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    RiscRecord.objects.create(risc=energy4, value=float(ecoq[6]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    if ecoq[7]:
                        RiscRecord.objects.create(risc=energy7, value=float(ecoq[7]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    else:
                        RiscRecord.objects.create(risc=energy7, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    if ecoq[8]:
                        RiscRecord.objects.create(risc=energy8, value=float(ecoq[8]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    else:
                        RiscRecord.objects.create(risc=energy8, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    if ecoq[9]:
                        RiscRecord.objects.create(risc=energy9, value=float(ecoq[9]), pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
                    else:
                        RiscRecord.objects.create(risc=energy9, value=0, pfc_market=pfc, file=pfc_data['eco_file'], year=int(ecoq[0]))
    return pfc


def get_last_pfc():
    snippets = PFC.objects.all()
    if not snippets:
        snippets = []
    reg_list = [{'id': pfc.id, 'pfc_id': datetime.strptime(pfc.pfc_id, '%d.%m.%Y'), 'created': pfc.created} for pfc in list(snippets)]
    records_list = sorted(reg_list, key=lambda x: x['pfc_id'], reverse=True)
    try:
        return PFC.objects.get(id=records_list[0]['id'])
    except:
        return None


def cockpit_update(pfc):

    records = PfcConsumptionRecord.objects.filter(pfc=pfc).values_list('interval_start', 'value').order_by('interval_start')

    year_nr = {
        k: len(list(g))
        for k, g in groupby(records, key=lambda i: i.interval_start.year)
    }
    year_sum = {
        k: sum(x.value for x in g)
        for k, g in groupby(records, key=lambda i: i.interval_start.year)
    }



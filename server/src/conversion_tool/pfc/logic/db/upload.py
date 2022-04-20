from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
from contextlib import closing
from django.db import connection

def upload_pfc_db(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='pfc_pfcconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'from_file_id', 'pfc_id', 'value', 'interval_start', 'interval', 'unit'),
        )

def upload_pfc_nofile_db(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='pfc_pfcconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'pfc_id', 'value', 'interval_start', 'interval', 'unit'),
        )

def upload_pfc_market_db(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='pfc_pfcmarketconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'from_file_id', 'pfc_market_id', 'value', 'interval_start', 'interval', 'unit'),
        )


def upload_pfcnofile_market_db(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='pfc_pfcmarketconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'pfc_market_id', 'value', 'interval_start', 'interval', 'unit'),
        )

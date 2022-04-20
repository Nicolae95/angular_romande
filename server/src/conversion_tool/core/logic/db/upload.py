from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
from contextlib import closing
from django.db import connection

def upload_db(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_energyconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'from_file_id', 'meter_id', 'value', 'interval_start', 'interval', 'unit'),
        )

def upload_null(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_energyconsumptionrecord',
            sep='\t',
            columns=('created', 'modified', 'meter_id', 'value', 'interval_start', 'interval', 'unit'),
        )

def upload_weekly(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_weeklyrecord',
            sep='\t',
            columns=('created', 'meter_id', 'year', 'hour', 'value', 'unit'),
        )

def upload_month(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_monthrecord',
            sep='\t',
            columns=('created', 'meter_id', 'schedule_id', 'year', 'month', 'value', 'unit'),
        )

def upload_sea(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_seasonrecord',
            sep='\t',
            columns=('created', 'meter_id', 'schedule_id', 'year', 'season', 'value', 'unit'),
        )

def upload_head(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='core_headgerecord',
            sep='\t',
            columns=('created', 'meter_id', 'schedule_id', 'year', 'value', 'unit'),
        )

from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
from contextlib import closing
from django.db import connection


def upload_med(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetmedrecord',
            sep='\t',
            columns=('created', 'budget_id', 'year', 'value', 'unit'),
        )

def upload_med_risc(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetmedwithriscsrecord',
            sep='\t',
            columns=('created', 'budget_id', 'year', 'value', 'unit'),
        )

def upload_med_season(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetmedseasonrecord',
            sep='\t',
            columns=('created', 'budget_id', 'season', 'schedule_id', 'year', 'value', 'unit'),
        )


def upload_med_maj_season(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetmedseasonmajorationrecord',
            sep='\t',
            columns=('created', 'budget_id', 'season', 'schedule_id', 'year', 'value', 'unit'),
        )


def upload_med_risc_season(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetmedseasonwithriscsrecord',
            sep='\t',
            columns=('created', 'budget_id', 'season', 'schedule_id', 'year', 'value', 'unit'),
        )

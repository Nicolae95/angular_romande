from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
from contextlib import closing
from django.db import connection

def upload_budget(stream):
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='budget_budgetrecord',
            sep='\t',
            columns=('created', 'budget_id', 'value', 'interval_start', 'interval', 'unit'),
        )

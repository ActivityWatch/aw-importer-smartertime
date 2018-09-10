import csv
from datetime import datetime, timedelta, timezone
import secrets

from tabulate import tabulate

from aw_core.models import Event


def parse(filepath):
    events = []
    with open(filepath, 'r') as f:
        c = csv.DictReader(f)
        for r in c:
            # print(r)
            dt = datetime.fromtimestamp(float(r['Timestamp']) / 1000)
            tz_h, tz_m = map(int, r['Time'].split("GMT+")[1].split()[0].split(":"))
            dt = dt.replace(tzinfo=timezone(timedelta(hours=tz_h, minutes=tz_m)))
            td = timedelta(milliseconds=float(r['Duration ms']))
            activity = r['Activity']
            device = r['Device']
            e = Event(timestamp=dt, duration=td, data={'activity': activity, 'device': device})
            events.append(e)
    return events


def import_as_bucket(filepath):
    events = parse(filepath)
    end = max(e.timestamp + e.duration for e in events)
    bucket = {
        'id': f'smartertime_import_{end.date()}_{secrets.token_hex(4)}',
        'events': events,
        'data': {
            'readonly': True,
        }
    }
    return bucket


def print_info(bucket):
    events = bucket['events']
    print(bucket['id'])
    print(bucket['data'])
    rows = []
    for a in ['Messenger', 'Plex', 'YouTube', 'Firefox', 'reddit']:
        rows.append([a, sum((e.duration for e in events if a in e.data['activity']), timedelta(0))])
    print(tabulate(rows, ['title', 'time']))


if __name__ == '__main__':
    bucket = import_as_bucket('timeslots.csv')
    print_info(bucket)

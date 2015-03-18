#!/usr/bin/python3

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import select
import time
import argparse
import os
import sys
import logging
import datetime

parser = argparse.ArgumentParser(
    prog = "pglistend",
    fromfile_prefix_chars = "@"
)

parser.add_argument('--channels', metavar='<channel>', required=True, type=str, nargs='+')
parser.add_argument('--signal-action-maps', metavar='<map>', required=True, type=str, nargs='+',
        help="maps of the form signal_name=exec")
parser.add_argument('--reconnect-delay', metavar='<seconds>', type=int, default=10)
parser.add_argument('--dsn', metavar='<dsn>', required=True, type=str, help="Database dsn (potgresql://...)")
parser.add_argument('--warn-missing-connection', metavar='<minutes>', type=int)

args = parser.parse_args()

""" Logging """

class AppFilter(logging.Filter):
    def filter(self, record):
        states = {
            logging.CRITICAL : 2,
            logging.ERROR : 3,
            logging.WARNING : 4,
            logging.INFO : 6,
            logging.DEBUG : 7
        }
        record.severity = states[record.levelno]
        return True

log = logging.Logger('pg')
log.addFilter(AppFilter())

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("<%(severity)s><%(levelname)s> %(message)s"))
log.addHandler(ch)

connection_lost = None

maps = {}
for mapping in args.signal_action_maps:
    signal, action = map(lambda x: x.strip(), mapping.split('='))
    
    if not os.path.isfile(action) or not os.access(action, os.X_OK):
        log.critical(
                "The path '{0}' does not represent an executable file"
                .format(action)
        )
        sys.exit(1)

    if signal not in maps:
        maps[signal] = []

    maps[signal].append(action)

def wait_for_notifications():
    conn = psycopg2.connect(args.dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    log.info("Connected to postgresql server")

    cur = conn.cursor()
    for channel in args.channels:
        cur.execute('LISTEN "{channel}";'.format(channel=channel))
        log.info("Listening to channel '{channel}'".format(channel=channel))

    connection_lost = None

    while True:
        select.select([conn],[],[])
        log.debug("Incomming data")
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop()
            signal = notify.payload
            log.debug("Got signal on channel '{channel}', action '{signal}'".format(
                    channel = notify.channel,
                    signal = signal
            ))
            if signal in maps:
                for action in maps[signal]:
                    log.info("Executing '{action}'".format(action=action))
                    status = os.system(action)
                    if status:
                        log.error("Exit status '{status}' of '{action}'"
                                .format(action=action,status=os.WEXITSTATUS(status)))

while True:
    try:
        wait_for_notifications()
    except psycopg2.OperationalError:
        log.debug("psycopg2.OperationalError, connection lost")

        if not connection_lost:
            connection_lost = datetime.datetime.now()
            last_report = datetime.datetime.now()
            log.info("Connection to postgresql server lost")

        else:
            delta = datetime.datetime.now() - connection_lost
            report_delta = datetime.datetime.now() - last_report
            if (report_delta.seconds >= 60*args.warn_missing_connection):
                last_report = datetime.datetime.now()
                log.warning("Not connected since {0} (duration)".format(delta))
                log.info("Reporting again in {0} minutes".format(1))
            
        log.debug("waiting {0}s before trying to reconnect"
                .format(args.reconnect_delay))
        time.sleep(args.reconnect_delay)
        log.debug("trying to reconnect")


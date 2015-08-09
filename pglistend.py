#!/usr/bin/python3

import psycopg2
import time
import os
import sys
import datetime
import pglisten.utils as utils
from pglisten.logging import log
from pglisten.params import args

connection_lost = None

maps = {}
# parse <signal> = <exec> format in signal_action_maps
for mapping in args.signal_action_maps:
    signal, action = map(lambda x: x.strip(), mapping.split('=', 1))
    
    # check if the action can be executed
    executable = action.split()[0]
    if not os.path.isfile(executable) or not os.access(executable, os.X_OK):
        log.critical(
                "The path '{0}' does not represent an executable file"
                .format(executable)
        )
        sys.exit(1)

    if signal not in maps:
        maps[signal] = []

    maps[signal].append(action)

while True:
    try:
        utils.wait_for_notifications(args, maps)
    except psycopg2.OperationalError as e:
        log.debug("psycopg2.OperationalError, connection lost: '{0}'".format(str(e)))

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
                log.info("Reporting again in {0} minutes".format(args.warn_missing_connection))
            
        log.debug("waiting {0}s before trying to reconnect"
                .format(args.reconnect_delay))
        time.sleep(args.reconnect_delay)
        log.debug("trying to reconnect")


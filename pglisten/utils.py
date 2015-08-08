from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
import select
import os
import time
import datetime
import fnmatch

from pglisten.logging import log

def wait_for_notifications(args, maps):
    conn = psycopg2.connect(args.dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    log.info("Connected to postgresql server")

    cur = conn.cursor()
    for channel in args.channels:
        cur.execute('LISTEN "{channel}";'.format(channel=channel))
        log.info("Listening to channel '{channel}'".format(channel=channel))

    connection_lost = None

    sleep_sec = 1
    last_action = datetime.datetime.now()

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
            for pattern in maps:
                if fnmatch.fnmatch(signal, pattern):
                    for action in maps[pattern]:
                        log.info("Executing '{action}'".format(action=action))
                        status = os.system(action)
                        if status:
                            log.error("Exit status '{status}' of '{action}'"
                                    .format(action=action,status=os.WEXITSTATUS(status)))

        diff = datetime.datetime.now() - last_action
        if diff.seconds > args.max_sleep:
            sleep_sec = 1

        last_action = datetime.datetime.now()
        log.debug("Sleeping {0} seconds".format(sleep_sec))
        time.sleep(sleep_sec)
        sleep_sec *= 2


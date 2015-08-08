Usage
=====

If using the *pglistend* executable, the following options can be
configured in */etc/pglistend.conf*. See *examples* folder for an config
and systemd service example. The following options might be used in the
config, or on the commandline if *pglistend.py* is used.

    usage: pglistend [-h] --channels <channel> [<channel> ...]
                     --signal-action-maps <map> [<map> ...]
                     [--reconnect-delay <seconds>] --dsn <dsn>
                     [--warn-missing-connection <minutes>] [--max-sleep <seconds>]

    optional arguments:
      -h, --help            show this help message and exit
      --channels <channel> [<channel> ...]
      --signal-action-maps <map> [<map> ...]
                            Maps of the form 'signal_payload=/bin/a /bin/b'. For
                            the signal_payload '*' and '?' are interpreted as
                            wildcards.
      --reconnect-delay <seconds>
      --dsn <dsn>           Database dsn (postgres://…)
      --warn-missing-connection <minutes>
      --max-sleep <seconds>

Required Debian Packages
========================

    apt install python3 python3-psycopg2

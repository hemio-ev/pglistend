# Usage

If using the pglistend, the following options can be configured in */etc/pglistend.conf*

```
usage: pglistend [-h] --channels <channel> [<channel> ...]
                 --signal-action-maps <map> [<map> ...]
                 [--reconnect-delay <seconds>] --dsn <dsn>
                 [--warn-missing-connection <minutes>]

optional arguments:
  -h, --help            show this help message and exit
  --channels <channel> [<channel> ...]
  --signal-action-maps <map> [<map> ...]
                        maps of the form signal_name=exec
  --reconnect-delay <seconds>
  --dsn <dsn>           Database dsn (potgresql://...)
  --warn-missing-connection <minutes>
```

# Dev

apt-get install python3 python3-psycopg2

import argparse

parser = argparse.ArgumentParser(
    prog = "pglistend",
    fromfile_prefix_chars = "@"
)

parser.add_argument('--channels', metavar='<channel>', required=True, type=str, nargs='+')
parser.add_argument('--signal-action-maps', metavar='<map>', required=True, type=str, nargs='+',
        help="Maps of the form 'signal_payload=/bin/a /bin/b'. For the signal_payload '*' and '?' are interpreted as wildcards.")
parser.add_argument('--reconnect-delay', metavar='<seconds>', type=int, default=20)
parser.add_argument('--dsn', metavar='<dsn>', required=True, type=str, help="Database dsn (postgres://…)")
parser.add_argument('--warn-missing-connection', metavar='<minutes>', default=30, type=int)
parser.add_argument('--max-sleep', metavar='<seconds>', default=30, type=int)

args = parser.parse_args()


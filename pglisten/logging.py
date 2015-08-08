import logging

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


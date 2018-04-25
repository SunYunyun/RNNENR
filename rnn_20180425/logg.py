import logging
from logging.handlers import RotatingFileHandler

Rthandler = RotatingFileHandler('rnn_reslut.log', maxBytes=10*1024*1024,backupCount=5)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)

def DEBUG(a,message=''):
    logging.warn('%s,%s'%(message,a))
DOMAIN = 'simple.xvm.mit.edu'
ADMIN_EMAIL_REDIRECT = 'easy@mit.edu'

# from Screener.py
LOG_ACCOUNT = 'simplemit@gmail.com'  # store emails for logging purposes
SPAM_ACCOUNT = 'simplemit.spam@gmail.com' # store emails that are blocked / spam
ROOT_EMAIL = 'root@' + DOMAIN # emails to this will get fwded to log

IP_MIN_BUFFER_TIME = 30 # Min seconds between emails from the same IP

DOMAIN_BLACKLIST = 'data/domain-blacklist.txt'
ADDRESS_BLACKLIST = 'data/address-blacklist.txt'

# from Processor.py
WEB_DOMAIN = DOMAIN
ADMIN_EMAIL = 'admin@' + DOMAIN # emails from SIMPLE are from this address

# from Sender.py
MAX_NUM_RCPTS = 2000
LOG_ACCOUNT = 'simplemit@gmail.com'  # store emails for logging purposes

# from Server.py
IP_ADDRESS = '18.181.1.186'
SMTP_PORT = 25
LOG_FILE = 'data/processor.log'


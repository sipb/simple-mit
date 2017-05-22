"""
Screener.py

Verifies messages that arrive to SIMPLE.
"""

import os, threading, time

LOG_ACCOUNT = 'simplemit@gmail.com'  # store emails for logging purposes
SPAM_ACCOUNT = 'simplemit.spam@gmail.com' # store emails that are blocked / spam
ROOT_EMAIL = 'root@simple.mit.edu'

# Min seconds between emails from the same IP
IP_MIN_BUFFER_TIME = 30

DOMAIN_BLACKLIST = 'data/domain-blacklist.txt'
ADDRESS_BLACKLIST = 'data/address-blacklist.txt'

class Screener(threading.Thread):

    # Sets up screener thread
    def __init__(self, ENV):
        threading.Thread.__init__(self)
        self.ENV = ENV
        if not ENV['test']:
            self.email_pool = ENV['db'].email_pool

        # map from IP address to times of sent emails
        self.ip_to_timestamp_map = {}

        # map from mailfrom to times of sent emails
        self.mailfrom_to_timestamp_map = {}

        self.domainBlacklist = []
        self.addressBlacklist = []

        # map from email address to time of most recent invalid email sent
        self.invalid_email_to_timestamp_map = {}

    # Runs a continuous loop to verify/flag unverified messages
    def run(self):
        while not self.ENV['stopped']:
            for message in self.email_pool.find({'status': 'UNVERIFIED'}):
                peer = message['peer']
                mailfrom = message['mailfrom']
                rcpttos = message['rcpttos']
                data = message['data']

                if self.is_blocked(mailfrom):
                    self.ENV['logger'].write(time.ctime() +
                            ' Blocked mail from %s %s addressed to %s\n'
                            % (mailfrom, peer, rcpttos))
                    self.ENV['sender'].redirect([SPAM_ACCOUNT], data)
                    self.email_pool.update({'_id': message['_id']},
                            {'$set': {'status': 'FLAGGED'}})
                elif rcpttos == [ROOT_EMAIL] or not self.delay(peer, mailfrom):
                    self.ENV['logger'].write(time.ctime() +
                            ' Received email from %s %s addressed to %s\n'
                            % (mailfrom, peer, rcpttos))
                    self.ENV['sender'].redirect([LOG_ACCOUNT], data)
                    self.email_pool.update({'_id': message['_id']},
                            {'$set': {'status': 'VERIFIED'}})

            time.sleep(5)


    def delay(self, peer, mailfrom):
        IP, port = peer
        current_time = time.time()

        if IP in self.ip_to_timestamp_map:
            sent_times = self.ip_to_timestamp_map[IP]
            # 2 emails cannot be sent within 10 seconds,
            # 3 emails cannot be sent within 30 seconds,
            # 4 emails cannot be sent within 90 seconds (1.5 minutes),
            #   and so on to
            # 10 emails cannot be sent within 65610 seconds (~18 hours).
            for i in range(min(8, len(sent_times))):
                if current_time - sent_times[-(i+1)] < 10 * (3 ** i):
                    return True
        else:
            self.ip_to_timestamp_map[IP] = []

        if mailfrom in self.mailfrom_to_timestamp_map:
            sent_times = self.mailfrom_to_timestamp_map[mailfrom]
            for i in range(min(8, len(sent_times))):
                if current_time - sent_times[-(i+1)] < 10 * (3 ** i):
                    return True
        else:
            self.mailfrom_to_timestamp_map[mailfrom] = []

        self.ip_to_timestamp_map[IP].append(current_time)
        self.mailfrom_to_timestamp_map[mailfrom].append(current_time)

        return False

    def is_blocked(self, mailfrom):
        if not self.domainBlacklist and os.path.exists(DOMAIN_BLACKLIST):
            self.domainBlacklist = [line.strip().lower() for line in open(DOMAIN_BLACKLIST,'r')]
        if not self.addressBlacklist and os.path.exists(ADDRESS_BLACKLIST):
            self.addressBlacklist = [line.strip().lower() for line in open(ADDRESS_BLACKLIST,'r')]

        # Not splitting + set lookup incase of extra formatting '<stuff@somedomainname>'
        for domain in self.domainBlacklist:
            if domain.lower() in mailfrom:
                return True

        for address in self.addressBlacklist:
            if address.lower() in mailfrom:
                return True

    def set_invalid_email(self, email):
        self.invalid_email_to_timestamp_map[email] = time.time()

    def is_valid_email(self, email):
        return email not in self.invalid_email_to_timestamp_map

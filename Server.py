"""
Server.py

The simple.mit.edu SMTP server that runs on Port 25.
"""

import smtpd, thread
from pymongo import MongoClient

from Sender import Sender
from Enumerator import Enumerator
from Parser import Parser
from Screener import Screener
from Processor import Processor
from SendlistServer import SendlistServer
from Config import IP_ADDRESS, SMTP_PORT, LOG_FILE

GLOBAL_ENV = {
        'stopped': False,
        'test': False,
        'send': True,
        }

class SimpleSMTPServer(smtpd.SMTPServer):

    # Overrides process_message() in smtpd.SMTPServer.
    #
    # This function is called whenever someone sends mail to simple.mit.edu.
    # e.g. processMessage((192.168.0.1, 25), 'kyc@mit.edu',
    #   ['{next}-{mjx}@simple.mit.edu'], "surprise party")
    #
    def process_message(self, peer, mailfrom, rcpttos, data):
        GLOBAL_ENV['db'].email_pool.insert({
            'peer': peer,
            'mailfrom': mailfrom,
            'rcpttos': rcpttos,
            'data': data,
            'status': 'UNVERIFIED',
            })

if __name__ == '__main__':
    # Initialize components
    GLOBAL_ENV['db'] = MongoClient().emails

    sender = Sender(GLOBAL_ENV)
    enumerator = Enumerator(GLOBAL_ENV)
    parser = Parser(GLOBAL_ENV)
    screener = Screener(GLOBAL_ENV)
    processor = Processor(GLOBAL_ENV)
    sendlist_server = SendlistServer(GLOBAL_ENV, IP_ADDRESS)

    # Initialize global environment
    GLOBAL_ENV['sender'] = sender
    GLOBAL_ENV['enumerator'] = enumerator
    GLOBAL_ENV['parser'] = parser
    GLOBAL_ENV['screener'] = screener
    GLOBAL_ENV['logger'] = open(LOG_FILE, 'a', 0)
    GLOBAL_ENV['processor'] = processor
    GLOBAL_ENV['sendlist_server'] = sendlist_server

    server = SimpleSMTPServer((IP_ADDRESS, SMTP_PORT), None)

    # Start new thread for the SMTP server.
    screener.start()
    processor.start()
    #sendlist_server.start() without SSL certs set up, webathena ain't gonna work
    import asyncore
    thread.start_new_thread(asyncore.loop, ())

    # Convenience commands to be run in the "terminal"
    def stop():
        GLOBAL_ENV['stopped'] = True
        #sendlist_server.stop()

    # Start "terminal" to enter any command
    while not GLOBAL_ENV['stopped']:
        try:
            exec(raw_input('> '))
        except Exception as e:
            print e


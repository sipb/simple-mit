"""
Processor.py

Processes each verified message that arrives to SIMPLE.
"""

import copy, os, random, re, string, threading, time
import Messages

from Config import ADMIN_EMAIL, WEB_DOMAIN

DRYRUN_EXTENSION = '.dryrun'
MITONLY_EXTENSION = '.mitonly'
INVALID_EMAIL_PATTERN = re.compile('<([^<>]+)>\.\.\. User unknown')

class Processor(threading.Thread):

    # Sets up a processor thread with a given environment and MongoDB client.
    def __init__(self, ENV):
        threading.Thread.__init__(self)
        self.ENV = ENV
        if not ENV['test']:
            self.email_pool = ENV['db'].email_pool


    # Runs a continuous loop to process verified messages
    def run(self):
        while not self.ENV['stopped']:
            for message in self.email_pool.find({'status': 'VERIFIED'}):
                result = self.process_message(message)
                new_status = 'FAILED' if 'error' in result else 'SENT'
                self.email_pool.update({'_id': message['_id']},
                        {'$set': {'status': new_status}})

            time.sleep(5)


    # Process a single message (with possibly multiple recipients)
    def process_message(self, message):
        single_rcpt = copy.copy(message)
        del single_rcpt['rcpttos']

        warnings = []
        for rcptto in message['rcpttos']:
            if DOMAIN in rcptto:
                single_rcpt['rcptto'] = rcptto
                result = self.__process_recipient(single_rcpt)
                if 'error' in result:
                    return {'error': result['error']}
                elif 'warnings' in result:
                    warnings.extend(result['warnings'])

        return {'warnings': warnings}


    # Process a single message addressed to a specific SIMPLE address
    def __process_recipient(self, message):
        flags = self.__get_flags(message)
        if self.__handle_special_emails(flags, message['data']):
            return {}
        print flags['local_part']
        result = self.ENV['parser'].parse(flags['local_part'], flags)

        return self.__send_result_email(flags, result, message)


    # Get flags from email address
    def __get_flags(self, message):
        rcptto = message['rcptto']
        data = message['data']

        flags = {}
        flags['to_admin'] = rcptto == ADMIN_EMAIL
        flags['to_root'] = rcptto == ROOT_EMAIL
        if flags['to_root']:
            matcher = INVALID_EMAIL_PATTERN.search(data)
            flags['invalid_email'] = matcher.group(1) if matcher else None
        flags['is_dryrun'] = (DRYRUN_EXTENSION + '@') in rcptto
        if flags['is_dryrun']:
            rcptto = rcptto.replace(DRYRUN_EXTENSION + '@', '@')
        flags['mit_only'] = (MITONLY_EXTENSION + '@') in rcptto
        if flags['mit_only']:
            rcptto = rcptto.replace(MITONLY_EXTENSION + '@', '@')
        flags['local_part'] = rcptto[:rcptto.index('@')]
        return flags


    # Handle special email address cases
    def __handle_special_emails(self, flags, data):
        if flags['to_admin']:
            self.ENV['sender'].redirect([ADMIN_EMAIL_REDIRECT], data)
            return True
        if flags['to_root']:
            if flags['invalid_email']:
                self.ENV['screener'].set_invalid_email(flags['invalid_email'])
                self.ENV['logger'].write('Setting invalid email %s\n' % flags['invalid_email'])
            return True
        return False


    # Given the result of the parsed SIMPLE address, sends the correct email.
    def __send_result_email(self, flags, result, message):
        mailfrom = message['mailfrom']
        rcptto = message['rcptto']
        data = message['data']

        if 'error' in result:
            self.__send_error_email(result['error'], mailfrom, rcptto)
            return {'error': result['error']}

        warnings = []
        if 'warnings' in result:
            fatal_email = self.__check_fatal_warnings(
                    result['warnings'], message)
            if fatal_email:
                self.__send_fatal_email(fatal_email, mailfrom, rcptto)
                return {'error': fatal_email}
            self.__send_warnings_email(result['warnings'], mailfrom, rcptto)
            warnings.extend(result['warnings'])

        if 'result' in result:
            if flags['is_dryrun']:
                self.__send_dryrun_email(result['dryrun'], mailfrom, rcptto)
            else:
                valid_emails = filter(self.ENV['screener'].is_valid_email,
                        result['result'])
                if flags['mit_only']:
                    valid_emails = filter(lambda x: '@mit' in x.lower(), 
                        valid_emails)
                self.__send_normal_email(valid_emails, data)

        return {'warnings': warnings}


    # Check if there are any fatal warnings that should be errors
    def __check_fatal_warnings(self, warnings, message):
        private_groups = []
        for warning in warnings:
            if warning[0] == 'PRIVATE':
                private_groups.append(warning[1])
        if private_groups:
            sendlist_link = 'link' if self.ENV['test'] else \
                    self.__generate_sendlist_link(private_groups, message)
            return Messages.PRIVATE_GROUP_ERROR % (
                    ''.join(private_groups), sendlist_link)

        for warning in warnings:
            if warning[0] == 'NONFUNCTIONING_SUBTRACT':
                return Messages.NONFUNCTIONING_SUBTRACT_ERROR


    # Generate a link that sends private list members to SIMPLE
    def __generate_sendlist_link(self, private_groups, message):
        mailfrom = message['mailfrom']
        rcptto = message['rcptto']

        self.ENV['logger'].write('Generating sendlist link for %s %s\n' % (private_groups, mailfrom))

        key = ''.join([random.choice(string.lowercase) for i in xrange(30)])

        self.ENV['db'].sendlist_links.insert({
            'key': key,
            'lists': private_groups,
            'message_id': message['_id'],
        })

        return 'https://' + WEB_DOMAIN + ':8103?key=' + key


    # Convenience functions for sending different types of emails
    def __send_error_email(self, error, mailfrom, rcptto):
        self.ENV['logger'].write('Error: %s\n' % error)
        self.ENV['sender'].send(ADMIN_EMAIL, mailfrom,
                "Error with your email to " + rcptto, error)

    def __send_fatal_email(self, message, mailfrom, rcptto):
        self.ENV['logger'].write('Action required\n')
        self.ENV['sender'].send(ADMIN_EMAIL, mailfrom,
                "Action required with your email to " + rcptto, message)

    def __send_warnings_email(self, warnings, mailfrom, rcptto):
        self.ENV['logger'].write('Warnings: %s\n' % warnings)
        self.ENV['sender'].send(ADMIN_EMAIL, mailfrom,
                "Warnings with your email to " + rcptto, ','.join(warnings))

    def __send_dryrun_email(self, results, mailfrom, rcptto):
        self.ENV['logger'].write('Sending dry run results\n')
        self.ENV['sender'].send(ADMIN_EMAIL, mailfrom,
                "Dryrun results for " + rcptto, results)

    def __send_normal_email(self, valid_emails, data):
        self.ENV['logger'].write('Sending to %s\n' % valid_emails)
        self.ENV['sender'].redirect(valid_emails, data)



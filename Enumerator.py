"""
Enumerator.py

Lists out the emails belonging to a given kerberos, email, or group.
"""

import subprocess
import Messages

FINGER = 'finger'
BLANCHE = './blanche'

def is_valid_group(group):
    return group and group[0].isalnum()

def is_mailman_list(group):
    return '@mailman.mit.edu' in group

def is_athena_mail(group):
    return '@athena.mit.edu' in group.lower()

def is_email(group):
    return '@' in group

def kerberos_to_email(kerberos):
    return kerberos + '@mit.edu'


class Enumerator:

    def __init__(self, ENV):
        self.ENV = ENV

    # Given a kerberos, email, or group, returns a list of the emails in that group.
    # e.g. list_emails('michaelx') returns ['michaelx@mit.edu']
    #      list_emails('michaeljxu@gmail.com') returns ['michaeljxu@gmail.com']
    #      list_emails('next-forum') returns [tommy@mit.edu, becky@mit.edu, ...]
    #
    def list_emails(self, group, env=None):
        # invalid token
        if not is_valid_group(group):
            return {'error': Messages.INVALID_TOKEN_PARSE_ERROR % group}

        # check for hard-coded group in database
        if not self.ENV['test']:
            entry = self.ENV['db'].list_members.find_one({'list': group})
            if entry:
                return self.__to_email_list(group, entry['members'])

        # check if the group is just an email
        if is_email(group):
            return {'result': [group]}

        # call finger
        out, err = subprocess.Popen([FINGER, group + '@athena.dialup.mit.edu'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        if err:  # error with finger call
            return {'error': Messages.FINGER_ERROR}

        if 'no such user' not in out:  # means 'group' is a kerberos
            return {'result': [kerberos_to_email(group)]}
    
        # call blanche
        if env:
            out, err = subprocess.Popen([BLANCHE, '-r', '-m', group.lower()],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).communicate()
        else:
            out, err = subprocess.Popen([BLANCHE, '-r', '-m', '-noauth', group.lower()],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        # check if there are real errors (other than blanche errors)
        for error in err.split('\n'):
            if error[:len(BLANCHE)] == BLANCHE:  # blanche error
                if 'No such list' in error:  # not kerberos or group; probably typo
                    return {'error': Messages.INVALID_GROUP_ERROR % group}
            elif error:
                return {'error': Messages.SYSTEM_ERROR}

        return self.__to_email_list(group, out)


    # Parse members string into list of emails
    def __to_email_list(self, group, members_string):
        emails = []
        for member in members_string.split('\n'):
            if is_mailman_list(member):
                return {'error': Messages.MAILMAN_ERROR % group}
            elif is_athena_mail(member):
                pass  # ignore KERBEROS: emails
            elif is_email(member):
                emails.append(member)
            elif member:  # is kerberos; add @mit.edu
                emails.append(kerberos_to_email(member))

        warnings = []
        if not emails:  # no results; probably private
            return {'error': Messages.PRIVATE_GROUP_ERROR_FATAL % group} # we can't deal with hidden lists rn
            # warnings.append(('PRIVATE', group))

        return {'result': emails, 'warnings': warnings}
    

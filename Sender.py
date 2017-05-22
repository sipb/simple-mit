"""
Sender.py

Sends the message to the specified recipients.
"""

import email, subprocess
import Messages

MAX_NUM_RCPTS = 2000
LOG_ACCOUNT = 'simplemit@gmail.com'  # store emails for logging purposes

FOOTER_AD = """\n\nThis email was sent using SIMPLE. Please visit simple.mit.edu/emails for
additional information, or contact admin@simple.mit.edu for
any questions/complaints."""

FOOTER = """\n\nThank you for using SIMPLE. Please visit simple.mit.edu/emails for
additional information, or contact admin@simple.mit.edu for
any questions/complaints."""

class Sender:

    def __init__(self, ENV):
        self.ENV = ENV

    # Sends the given message.
    # e.g. send(['tommy@mit.edu', 'becky@mit.edu', ...], "surprise party")
    #   will send the message to tommy, becky, etc.
    #
    def send_message(self, rcpt_emails, data):
        if not self.ENV['send']:
            return
        data = data.encode('ascii', 'ignore')

        p = subprocess.Popen(['sendmail', ','.join(rcpt_emails)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate(input=data + '\n.\n')  # a line with a single period ends sendmail
        if stderr:
            return {'error': Messages.SEND_MAIL_FAILURE}
        else:
            return {'result': Messages.SEND_MAIL_SUCCESS}


    # Redirects the given message to the intended recipients.
    def redirect(self, rcpt_emails, data):
        if len(rcpt_emails) > MAX_NUM_RCPTS:
            return {'error': Messages.TOO_MANY_RCPTS}

        # attach footer_ad to the email
        msg = email.message_from_string(data.encode('ascii', 'ignore'))
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                part.set_payload(part.get_payload() + FOOTER_AD)
            elif part.get_content_type() == 'text/html':
                part.set_payload(part.get_payload() + FOOTER_AD.replace('\n', '<br/>'))
        data = msg.as_string()

        return self.send_message(rcpt_emails, data)


    # Replies to a specific recipient, with the given subject and message.
    def send(self, mailfrom, rcptto, subject, message):
        data = """From: %s\nTo: %s\nSubject: %s\n\n%s%s""" \
                % (mailfrom, rcptto, subject, message, FOOTER)

        return self.send_message([rcptto, LOG_ACCOUNT], data)


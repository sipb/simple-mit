"""
Stores all strings, including log strings, warnings, and error messages.
"""

MAILMAN_ERROR = """Error: %s is a mailman list. SIMPLE is currently unable to process
mailman lists."""

PRIVATE_GROUP_ERROR = """%s is a hidden list, whose members SIMPLE is unable to access.
If you have the credentials to view the members of the list,
please visit the following link to send the list members to SIMPLE:

%s

NOTE: the link uses the Webathena interface to securely
ask for your kerberos password. Your password will NOT be
sent to SIMPLE or any other external machines."""

PRIVATE_GROUP_ERROR_FATAL = """%s is a hidden list, whose members SIMPLE is unable to access.
Using SIMPLE with hidden lists is a feature under maintenance, sorry :/"""

FINGER_ERROR = """Error: the MIT directory is temporarily down. Please try sending your email =
again in a few minutes. Note: your email was NOT sent."""

SYSTEM_ERROR = """An unexpected error occurred and your mail was not sent. Please try
again later."""

MULTIPLE_OPERATORS_PARSE_ERROR = """Error: invalid email, more than one operator in a row: %s"""

MISSING_GROUP_PARSE_ERROR = """Error: invalid email, expect a kerberos/email/mailing list."""

MISSING_OPERATOR_PARSE_ERROR = """Error: invalid email, expect operator between two
kerberos/emails/mailing lists."""

INVALID_TOKEN_PARSE_ERROR = """Error: invalid token %s found in the email."""

INVALID_OPERATOR_PARSE_ERROR = """Error: invalid operator %s found in the email."""

MISMATCHED_BRACES_PARSE_ERROR = """Error: mismatched braces in email expression."""

INVALID_GROUP_ERROR = """Error: %s does not appear to be a kerberos, email, or mailing list.
Perhaps you made a typo? Note: your email was NOT sent."""

NONFUNCTIONING_SUBTRACT_ERROR = """Error: subtracting two mutually exclusive email lists.
Perhaps you made a typo? Note: your email was NOT sent.

Note: this error sometimes occurs when MIT directory is down and returns an empty list.
In that case, please try sending your email again."""

SERVER_START_MESSAGE = "Credentials verified and SIMPLE server started."

SEND_MAIL_SUCCESS = "Successfully sent mail."""

SEND_MAIL_FAILURE = "Failed to send mail."""

TOO_MANY_RCPTS = """Error: your email includes too many recipients (over 2000). Please
try again with another query. Note: your email was NOT sent."""

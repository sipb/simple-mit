#!/bin/bash

# Start the SIMPLE Server.
# Requires root permissions.

BLANCHE="./blanche"
BLANCHE_LIB1="/usr/lib/libmrclient.so.0"
BLANCHE_LIB2="/usr/lib/libmoira.so.0"
BLANCHE_LIB3="/usr/lib/libhesiod.so.0"

POSTFIX="postfix"
POSTFIX_MASTER_FILE="/etc/postfix/master.cf"
POSTFIX_RESOLV_FILE="/var/spool/postfix/etc/resolv.conf"

SPACES="[[:space:]][[:space:]]*"

DOMAIN=`hostname -f`
NOTIFY_TO_ADDR="easy@mit.edu"
NOTIFY_FROM_ADDR="admin@$DOMAIN"

# Check that we are using sudo.
if [ $(whoami) != "root" ]
then
    echo "Error: run this script with sudo."
    exit 1
fi


# Check static IP setup.
echo "NOT checking that domain and static IP are configured correctly. Check that on your own."

# Checking blanche.
echo "Checking that blanche is set up correctly..."

if [ ! -e $BLANCHE ]
then
    echo -e "Error: copy the blanche binary from Athena into the simple-server directory:\\n\\nscp kyc2915@athena.dialup.mit.edu:/usr/bin/blanche .\\n"
    exit 1
fi

if [ ! -e $BLANCHE_LIB1 ] || [ ! -e $BLANCHE_LIB2 ] || [ ! -e $BLANCHE_LIB3 ]
then
    echo -e "Error: copy the following libraries from Athena into /usr/lib:\\n\\n$BLANCHE_LIB1\\n$BLANCHE_LIB2\\n$BLANCHE_LIB3\\n"
    exit 1
fi

if ! $BLANCHE -r -m -noauth $ADMIN_EMAIL_REDIRECT > /dev/null
then
    echo -e "Error: test blanche query failed.\\n\\nIs $BLANCHE the correct blanche binary?\\nDo you have internet connection?\\n"
    exit 1
fi


# Checking postfix.
echo "Checking that postfix is set up correctly..."
POSTFIX_CHANGED=false

if ! which $POSTFIX > /dev/null
then
    echo -e "Error: postfix not installed. Run the following:\\n\\nsudo apt-get install postfix\\n"
    exit 1
fi

if grep -q "^smtp$SPACES.*smtpd$" $POSTFIX_MASTER_FILE
then
    echo "Reassigning postfix port in $POSTFIX_MASTER_FILE..."
    # Replace the smtp keyword with the port 1025
    sed -i -e "/^smtp\s.*smtpd$/ s/^smtp/1025/" $POSTFIX_MASTER_FILE
    POSTFIX_CHANGED=true
fi

if ! diff $RESOLV_FILE $POSTFIX_RESOLV_FILE
then
    echo "Copying $RESOLV_FILE to $POSTFIX_RESOLV_FILE..."
    cp $RESOLV_FILE $POSTFIX_RESOLV_FILE
    POSTFIX_CHANGED=true
fi


# Ensure postfix has started/reloaded.
if $POSTFIX_CHANGED
then
    if $POSTFIX status > /dev/null
    then
        $POSTFIX reload
    else
        $POSTFIX start
    fi
fi


# Check for Sendlist server requirements
if ! python -c "import cherrypy"
then
    echo "Error: cherrypy not installed."
    exit 1
fi
if [ ! -e sendlist/key.pem ]
then
    echo "Warning: key.pem not found."
#    exit 1
fi
if [ ! -e sendlist/cert.pem ]
then
    echo "Warning: cert.pem not found."
#    exit 1
fi


# Run tests
echo "Running tests..."
if ! python Tests.py
then
    exit 1
fi


# Start the Server python script!
echo "Starting server..."
echo -e "From: $NOTIFY_FROM_ADDR\\nTo: $NOTIFY_TO_ADDR\\nSubject: The server at $DOMAIN has started\\nThis is an automatic notification that the server has been started.\\n." | sendmail $NOTIFY_TO_ADDR
python Server.py


# Is called when the Server dies.
echo -e "From: $NOTIFY_FROM_ADDR\\nTo: $NOTIFY_TO_ADDR\\nSubject: The server at $DOMAIN has ended\\nThis may be due either to someone manually stopping the server, or to the server abruptly crashing.\\n." | sendmail $NOTIFY_TO_ADDR


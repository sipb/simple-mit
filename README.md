See www/index.html for the real intro to the project.

Files that have config things that might need to be changed

enumeratorTest: check lists
processor: domain, admin_email_redirect, admin_email?, root_email?
screener: log_account, spam_account, root_email?
sender: log_account
server: ip_address
tests: check lists
start_server.sh: name, ip, admin_email_redirect

Spun up a fresh XVM with Ubuntu Trusty.
Needed to install debathena-libmoira, and debathena-libmrclient.
Needed to symlink to libhesiod.so.0 from /usr/lib because it was in /usr/lib/x86_blahblahblah.
Needed to install postfix (and configured it as "Internet site: Mail is sent and received directly using SMTP".)
Set "system mail name" to simple.xvm.mit.edu when configuring postfix. This might need to change.
Needed to install python-cherrypy3.
Needed to install finger.
Needed to install pymongo.
Needed to install mongodb-server.
Decided to install openssh-server. Set up a key so I could ssh to root from my laptop.
Needed to install python-openssl.

Commented out the "launch web server" part of the code, as well as the part of the launch script which

TODOS:
- make server run permanently, either via systemd or via screen
- make configuration not distributed across a bunch of files
- make the test suite more robust to kevin chen graduating
- re-enable limited web server functionality (without SSL because we're still waiting on certs for that)
- check that root and admin emails work the way they should
- check that special characters in email addresses work the way they should
- get an afs quota from sipb so it's not running on sadun's personal quota
- once we get simple.mit.edu, (a) get certs, (b) maaaaybe implement kerberos auth ew

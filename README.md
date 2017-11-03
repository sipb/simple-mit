See www/index.html for the real intro to SIMPLE. tl;dr it's an email list enhancement suite.

This codebase is the one running on simple.xvm.mit.edu. Steps that have had to be taken on the machine to set this up:
- Spun up a fresh XVM with Ubuntu Trusty. Installed openssh-server for easier maintenance.
- Installed debathena-libmoira, and debathena-libmrclient, python-cherrypy3, finger, pymongo, mongodb-server, python-openssl.
- Installed postfix, and when configuring set "system mail name" to simple.xvm.mit.edu.
- Twiddled the configuration parameters in various files (particularly Processor.py, Server.py, and start_server.sh) to accommodate domain and IP changes.
- Made a symlink at /usr/lib/libhesiod.so.0 because the real deal was in /usr/lib/x86_blahblahblah.

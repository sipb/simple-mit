import base64, cherrypy, json, os, struct, threading
from tempfile import NamedTemporaryFile
from Enumerator import Enumerator

SENDLIST_PORT = 8103

# Some DER encoding stuff. Bleh. This is because the ccache contains a
# DER-encoded krb5 Ticket structure, whereas Webathena deserializes
# into the various fields. Re-encoding in the client would be easy as
# there is already an ASN.1 implementation, but in the interest of
# limiting MIT Kerberos's exposure to malformed ccaches, encode it
# ourselves. To that end, here's the laziest DER encoder ever.
def der_encode_length(l):
    if l <= 127:
        return chr(l)
    out = ""
    while l > 0:
        out = chr(l & 0xff) + out
        l >>= 8
    out = chr(len(out) | 0x80) + out
    return out

def der_encode_tlv(tag, value):
    return chr(tag) + der_encode_length(len(value)) + value

def der_encode_integer_value(val):
    if not isinstance(val, (int, long)):
        raise TypeError("int")
    # base 256, MSB first, two's complement, minimum number of octets
    # necessary. This has a number of annoying edge cases:
    # * 0 and -1 are 0x00 and 0xFF, not the empty string.
    # * 255 is 0x00 0xFF, not 0xFF
    # * -256 is 0xFF 0x00, not 0x00

    # Special-case to avoid an empty encoding.
    if val == 0:
        return "\x00"
    sign = 0 # What you would get if you sign-extended the current high bit.
    out = ""
    # We can stop once sign-extension matches the remaining value.
    while val != sign:
        byte = val & 0xff
        out = chr(byte) + out
        sign = -1 if byte & 0x80 == 0x80 else 0
        val >>= 8
    return out

def der_encode_integer(val):
    return der_encode_tlv(0x02, der_encode_integer_value(val))
def der_encode_int32(val):
    if val < -2147483648 or val > 2147483647:
        raise ValueError("Bad value")
    return der_encode_integer(val)
def der_encode_uint32(val):
    if val < 0 or val > 4294967295:
        raise ValueError("Bad value")
    return der_encode_integer(val)

def der_encode_string(val):
    if not isinstance(val, unicode):
        raise TypeError("unicode")
    return der_encode_tlv(0x1b, val.encode("utf-8"))

def der_encode_octet_string(val):
    if not isinstance(val, str):
        raise TypeError("str")
    return der_encode_tlv(0x04, val)

def der_encode_sequence(tlvs, tagged=True):
    body = []
    for i, tlv in enumerate(tlvs):
        # Missing optional elements represented as None.
        if not tlv:
            continue
        if tagged:
            # Assume kerberos-style explicit tagging of components.
            tlv = der_encode_tlv(0xa0 | i, tlv)
        body.append(tlv)
    return der_encode_tlv(0x30, "".join(body))

def der_encode_ticket(tkt):
    return der_encode_tlv(
        0x61, # Ticket
        der_encode_sequence(
            [der_encode_integer(5), # tktVno
             der_encode_string(tkt["realm"]),
             der_encode_sequence( # PrincipalName
                    [der_encode_int32(tkt["sname"]["nameType"]),
                     der_encode_sequence([der_encode_string(c)
                                          for c in tkt["sname"]["nameString"]],
                                         tagged=False)]),
             der_encode_sequence( # EncryptedData
                    [der_encode_int32(tkt["encPart"]["etype"]),
                     (der_encode_uint32(tkt["encPart"]["kvno"])
                      if "kvno" in tkt["encPart"]
                      else None),
                     der_encode_octet_string(
                                base64.b64decode(tkt["encPart"]["cipher"]))])]))

# Kerberos ccache writing code. Using format documentation from here:
# http://www.gnu.org/software/shishi/manual/html_node/The-Credential-Cache-Binary-File-Format.html

def ccache_counted_octet_string(data):
    if not isinstance(data, str):
        raise TypeError("str")
    return struct.pack("!I", len(data)) + data

def ccache_principal(name, realm):
    header = struct.pack("!II", name["nameType"], len(name["nameString"]))
    return (header + ccache_counted_octet_string(realm.encode("utf-8")) +
            "".join(ccache_counted_octet_string(c.encode("utf-8"))
                    for c in name["nameString"]))

def ccache_key(key):
    return (struct.pack("!H", key["keytype"]) +
            ccache_counted_octet_string(base64.b64decode(key["keyvalue"])))

def flags_to_uint32(flags):
    ret = 0
    for i, v in enumerate(flags):
        if v:
            ret |= 1 << (31 - i)
    return ret

def ccache_credential(cred):
    out = ccache_principal(cred["cname"], cred["crealm"])
    out += ccache_principal(cred["sname"], cred["srealm"])
    out += ccache_key(cred["key"])
    out += struct.pack("!IIII",
                       cred["authtime"] // 1000,
                       cred.get("starttime", cred["authtime"]) // 1000,
                       cred["endtime"] // 1000,
                       cred.get("renewTill", 0) // 1000)
    out += struct.pack("!B", 0)
    out += struct.pack("!I", flags_to_uint32(cred["flags"]))
    # TODO: Care about addrs or authdata? Former is "caddr" key.
    out += struct.pack("!II", 0, 0)
    out += ccache_counted_octet_string(der_encode_ticket(cred["ticket"]))
    # No second_ticket.
    out += ccache_counted_octet_string("")
    return out

def make_ccache(cred):
    # Do we need a DeltaTime header? The ccache I get just puts zero
    # in there, so do the same.
    out = struct.pack("!HHHHII",
                      0x0504, # file_format_version
                      12, # headerlen
                      1, # tag (DeltaTime)
                      8, # taglen (two uint32_ts)
                      0, 0, # time_offset / usec_offset
                      )
    out += ccache_principal(cred["cname"], cred["crealm"])
    out += ccache_credential(cred)
    return out


class SendlistServer(threading.Thread):

    def __init__(self, ENV, IP_ADDRESS):
        threading.Thread.__init__(self)
        self.ENV = ENV
        server_config = {
                'server.socket_host' : IP_ADDRESS,
                'server.socket_port' : SENDLIST_PORT,
		
		# If you haven't set up SSL certs, don't bother running the sendlist server.
                'server.ssl_module' : 'pyopenssl',
                'server.ssl_certificate' : 'sendlist/cert.pem',
                'server.ssl_private_key' : 'sendlist/key.pem',
                'server.ssl_certificate_chain' : 'sendlist/certchain.pem',
                }
        cherrypy.config.update(server_config)

    def get_sendlist_link(self, key):
        return self.ENV['db'].sendlist_links.find_one({'key': key})

    # Look up all the mailing lists using user's credentials
    # Returns {'valid': [lists], 'invalid': [lists]}
    def lookup_lists(self, key, cred):
        request = self.get_sendlist_link(key)
        with NamedTemporaryFile(prefix="siab_ccache_") as ccache:
            # Write the credentials into a krb5 ccache.
            ccache.write(make_ccache(cred))
            ccache.flush()

            # Use Enumerator to get mailing list members
            enumerator = Enumerator({'test': True})
            env = dict(os.environ)
            env['KRB5CCNAME'] = ccache.name
            valid = []
            for mailing_list in request['lists']:
                result = enumerator.list_emails(mailing_list, env)
                if 'error' not in result and len(result['warnings']) == 0:
                    self.ENV['db'].list_members.update(
                            {'list': mailing_list},
                            {'$set': {'members': '\n'.join(result['result'])}},
                            upsert=True)
                    valid.append(mailing_list)

            # Check whether all lists have known members
            invalid = []
            for mailing_list in request['lists']:
                if not self.ENV['db'].list_members.find_one({'list': mailing_list}):
                    invalid.append(mailing_list)
            sent = len(invalid) == 0
            if sent:
                self.ENV['db'].email_pool.update(
                        {'_id': request['message_id'], 'status': 'FAILED'},
                        {'$set': {'status': 'VERIFIED'}})

            return {'valid': ', '.join(valid), 'invalid': ', '.join(invalid), 'sent': sent}

    def run(self):
        conf = {
                '/': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.root': os.path.join(os.getcwd(), 'sendlist'),
                    'tools.staticdir.dir': 'static'
                    }
                }
        cherrypy.quickstart(self, '/', conf)

    def stop(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    def index(self, key):
        html = open('sendlist/webathena.html').read()
        html = html.replace('<%= key %>', key)
        lists = ', '.join(self.get_sendlist_link(key)['lists'])
        html = html.replace('<%= lists %>', lists)
        return html

    @cherrypy.expose
    def sendlist(self):
        if cherrypy.request.method == 'POST':
            cl = cherrypy.request.headers['Content-Length']
            rawbody = cherrypy.request.body.read(int(cl))
            body = json.loads(rawbody)
            result = self.lookup_lists(body['key'], body['cred'])
            return ('Complete.\n' +
                    'Successfully retrieved lists: %s\n' +
                    'Unsuccessfully retrieved lists: %s\n') % \
                            (result['valid'], result['invalid']) + \
                            ('Your email has been sent.' if result['sent']
                                    else 'Your email has NOT been sent.')

if __name__ == '__main__':
    from pymongo import MongoClient
    SendlistServer({'db': MongoClient().emails}, '127.0.0.1').start()

#!/usr/bin/env python2.7

import cgitb; cgitb.enable() # Comment out to disable web tracebacks
import cgi
import ldap
import logging
import os
import sys

# Log the user's old password (useful for determining if the user is mistyping
# a randomly generated password, for example)
LOG_OLD_PASSWORDS = True

# Remove a user from a group once they've set their password
REMOVE_FROM_GROUP = True

LDAP_SERVER = "ldaps://contoso.com:636"
LDAP_DOMAIN = "CONTOSO"

# Your domain's root certificate (because we're using SSL to connect to LDAP)
LDAP_CERT_FILE = "/etc/ssl/certs/root-ca.crt"

# Where to search for users in Active Directory
LDAP_SEARCH_ROOT = "DC=contoso,DC=com"

# The group to remove the user from (this is a great way to enforce security
# constraints for external users who haven't changed their generated password)
LDAP_GROUP_TO_REMOVE = "CN=Default Password Holder,OU=Security Groups,DC=contoso,DC=com"

logging.basicConfig(filename="password.log", level=logging.INFO,
    format="%(asctime)-15s %(levelname)-5s %(ip)-15s %(apache_user)s/%(script_user)s %(message)s")

print "Content-Type: text/html\n\n"

form = cgi.FieldStorage()

if "username" not in form or "old_password" not in form \
        or "new_password" not in form \
        or "new_password_verify" not in form:
    print "Please enter all form fields."

    sys.exit(1)

username = form.getvalue("username")

old_password = form.getvalue("old_password")
new_password = form.getvalue("new_password")

new_password_verify = form.getvalue("new_password_verify")

log_info = {
    'script_user': username,
    'apache_user': os.environ.get('REMOTE_USER', 'Unknown'),
    'ip': os.environ.get('REMOTE_ADDR', 'Unknown')
}

log = logging.LoggerAdapter(logging.getLogger("password.py"), log_info)

if LOG_OLD_PASSWORDS:
    log.info("Old password: %s" % old_password)

if new_password != new_password_verify:
    print "Your new passwords do not match."

    sys.exit(1)

try:
    ldap.set_option(ldap.OPT_REFERRALS, 0)

    ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, LDAP_CERT_FILE)
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 1)

    l = ldap.initialize(LDAP_SERVER)

    l.protocol_version = ldap.VERSION3

    l.simple_bind_s("%s\%s" % (LDAP_DOMAIN, username), old_password)

    r = l.search_s(LDAP_SEARCH_ROOT, ldap.SCOPE_SUBTREE,
        "(sAMAccountName=%s)" % username, ['distinguishedName'])

    if not len(r) == 1:
        raise Exception

    dn = r[0][0]

    old_password = ('"%s"' % old_password).encode("utf-16-le")
    new_password = ('"%s"' % new_password).encode("utf-16-le")

    attributes = [(ldap.MOD_DELETE, 'unicodePwd', old_password),
                  (ldap.MOD_ADD, 'unicodePwd', new_password)]

    l.modify_s(dn, attributes)

    log.info("Changed password successfully.")

    print "Your password was changed successfully.<br />"
except ldap.LDAPError, e:
    log.error("LDAP exception encountered.", exc_info=True)

    print '<abbr title="%s">Sorry, your password was unable to be changed.</abbr><br />' % e

    sys.exit(1)

if REMOVE_FROM_GROUP:
    exists_in_group = 0

    try:
        exists_in_group = l.compare_s(LDAP_GROUP_TO_REMOVE, 'member', dn)
    except:
        pass

    if exists_in_group:
        try:
            g_attributes = [(ldap.MOD_DELETE, 'member', dn)]

            l.modify_s(LDAP_GROUP_TO_REMOVE, g_attributes)

            log.info("Removed from '%s' group successfully." %
                LDAP_GROUP_TO_REMOVE)

            print "Your account permissions have been enabled."

            l.unbind()
        except ldap.LDAPError, e:
            log.error("LDAP exception encountered.", exc_info=True)

            print '<abbr title="%s"><em>However, we were unable to enable your account permissions.</em></abbr>' % e

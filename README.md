password-self-service
=====================

These scripts are designed to let internal and external users change their Active Directory passwords.

For it to work securely _you must use SSL on the webserver and for the LDAP connection_.

It looks like this:

![password-self-service](http://i.imgur.com/H6If1.png)

Configuration
-------------

Modify the configuration variables in `password.py` and provide some explanatory text in `index.html`.

You may also wish to change the password complexity requirements in `passwords.js`.

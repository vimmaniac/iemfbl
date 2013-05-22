# List your domain names and related mailbox file
# in the following dictionary. For example -
#
# DOMAIN_AND_MAILBOX = {
#     'email1.example.com' : '/var/mail/foobar' ,
#     'massmailer.example.com' : '/var/mail/joe' ,
# }
#
# Note that, the colon ":" in the middle and
# the comma "," at the end are mandatory.
DOMAIN_AND_MAILBOX = {

   'email1.example.com' : '/var/mail/foobar' ,

   'massmailer.example.com' : '/var/mail/joe' ,

}

# Number of simultaneous http connections. Setting it
# to too high may overload the server.
N_HTTP_CONNECTIONS = 50


# Time between two successive mailbox check, in seconds.
PERIODIC_CHECK_INTERVAL = 120

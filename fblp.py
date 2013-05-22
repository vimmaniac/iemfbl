#########################################################################
# Name: FeedBackLoopProcessor
#
# FileName: fblp.py
#
# Version: 1.0
#
# Usage: This program periodically inspects a mailbox for incoming
#        feedback loop mail in ARF (Abuse Report Format). When it
#        finds an abuse report, it extracts the 'List-Unsubscribe'
#        field from the original mail and sends an http request,
#        effectively unsubscribing the reporting user.
#
# License: This program is distributed under the terms of GNU LGPL
#          license. Please visit the following link to see the 
#          license text in LICENSE.txt or visit the following link -
#          http://www.gnu.org/licenses/lgpl.txt
#
# Author: Titon Barua <titanix88@gmail.com>
#
# Copyright: Vimmaniac Private Limited <vimmaniac@gmail.com>, Bangladesh.
#
# Date: 2nd May, 2012.
#
# Note: python2.7 with greetlet package is required to run this script.
#       Alternatively, python pypy interpreter is recommended.
#########################################################################
import re
import shelve
import mailbox
import string
import uuid
import os.path
import datetime
import time
import sys

import eventlet
from eventlet.green import urllib2

from fblp_config import DOMAIN_AND_MAILBOX
from fblp_config import N_HTTP_CONNECTIONS
from fblp_config import PERIODIC_CHECK_INTERVAL

PERSISTENT_DIR = 'persistent'

# List of supported mailbox class.
SUPPORTED_MAILBOX_CLASS = (mailbox.mbox, mailbox.Maildir)


class UnsupportedMailboxFormat(Exception):
    def __init__(self, mailbox_path):
        self._mbpath = mailbox_path

    def __unicode__(self):
        return ('The mailbox given ({0}) is of unsupported type.'
                .format(self._mbpath))


class FeedbackLoopProcessor(object):
    def _get_urldb_name(self):
        def only_alnum(c):
            if (c in string.letters) or (c in string.digits):
                return c
            else:
                return '_'

        return os.path.join(
                   os.path.realpath(os.path.dirname(sys.argv[0])),
                   self._persistent_dir,
                   ''.join(map(only_alnum,
                               self._domain+'_'+self._mailbox_path)))


    def __init__(self, domain, mailbox_path, persistent_dir, greenlet_pool):
        self._domain = domain
        self._mailbox_path = mailbox_path
        self._persistent_dir = persistent_dir
        self._greenlet_pool = greenlet_pool
        
        self._mailbox = None

        # Open a shelve to store unsubscribe links.
        self._urldb = shelve.open(self._get_urldb_name())

        self._crx_is_abuse_mail = re.compile(
            r'^Feedback-Type: *Abuse$', re.I | re.M)

        self._crx_find_list_unsubscribe_link = re.compile(
            r'^List-Unsubscribe: *<(http://{0}.*?)>$'
            .format(self._domain), re.I | re.M)

        self._mailbox_class_list = SUPPORTED_MAILBOX_CLASS



    def __del__(self):
        # Close the shelve.
        self._urldb.close()


    def _open_mailbox(self):
        self._mailbox = None

        # Try every mailbox type supported until
        # finding the apropriate one.
        for mailbox_class in self._mailbox_class_list:
            try:
                self._mailbox = mailbox_class(
                    self._mailbox_path, create=False)
                break

            # We should try another mailbox format.
            except (mailbox.FormatError, IOError):
                continue

        if self._mailbox is None:
            raise UnsupportedMailboxFormat(mailbox_path)

        if len(self._mailbox_class_list) > 0:
            self._mailbox_class_list = (mailbox_class,)


    def _check_mailbox(self):
        n_new_uslinks = 0
        for mailkey in self._mailbox.iterkeys():
            mail_ = self._mailbox.get_string(mailkey)

            match = self._crx_is_abuse_mail.search(mail_)
            if match is None: continue

            match = self._crx_find_list_unsubscribe_link.search(mail_)
            if match is None: continue

            self._urldb[str(uuid.uuid1())] = str(match.group(1))
            self._mailbox.remove(mailkey)
            
            n_new_uslinks += 1

        return n_new_uslinks


    def _click_link(self, urlitem):
        key, url = urlitem
        try:
            urllib2.urlopen(url).read()
            print("Successfully clicked link: {0}".format(url))
            return key

        except IOError as e:
            print("({0}) Error while clicking link: {1}".format(e, url))
            return None


    def process(self):
        print("Checking mailbox: {0}".format(self._mailbox_path))
        n_new_uslinks = 0

        try:
            self._open_mailbox()
            self._mailbox.lock()

            n_new_uslinks = self._check_mailbox()
            if n_new_uslinks > 0:
                print("Collected {0} new unsubscribe links."
                      .format(n_new_uslinks))

        except mailbox.ExternalClashError as e:
            print("The mailbox is currently locked by other programs.")

        finally:
            if isinstance(self._mailbox, mailbox.Mailbox):
                self._mailbox.unlock()
                self._mailbox.close()

        clicked_link_ids = self._greenlet_pool.imap(
                               self._click_link, self._urldb.items())

        for link_id in clicked_link_ids:
            if link_id is None: continue

            del self._urldb[link_id]


if __name__ == '__main__':
    pool = eventlet.GreenPool(size=N_HTTP_CONNECTIONS)
    fblps = [FeedbackLoopProcessor(domain, mailbox_, PERSISTENT_DIR, pool)
             for (domain, mailbox_) in DOMAIN_AND_MAILBOX.items()]

    try:
        while True:
            start_time = datetime.datetime.utcnow()
            print("Checking started at {0}".format(start_time))

            for fblp in fblps:
                fblp.process()

            end_time = datetime.datetime.utcnow()
            sleep_time = (PERIODIC_CHECK_INTERVAL
                          - (end_time - start_time).seconds)

            print("Checking finished at {0}".format(end_time))

            if sleep_time > 0:
                time.sleep(sleep_time)

    except (SystemExit, KeyboardInterrupt) as e:
        print("Quiting ...")
        sys.exit(0)

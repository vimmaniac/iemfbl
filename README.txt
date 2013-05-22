INSTALLATION
============
To run the program, it is recommended to use a particular
python interpreter "pypy". You can download pypy from the
following link -

    http://pypy.org/download.html

Installing pypy is simply a matter of unpacking it in a
directory. Unpack feedbackloopprocessor.tar.gz to
another suitable location. Then simply run the following
command to run the script -

    <pypy_dir>/bin/pypy <feedbackloopprocessor_dir>/fblp.py

You can specify mailbox path and associated domain in the
fblp_config.py file. Note that, this script is designed
to be run indefinitely as it resumes after every specified
interval and checks the mailbox. You should not run it
as a cron job.

Supported mailbox formats are "Maildir" and "MBox". As the
script automatically deletes feedback mails after extracting
unsubscribe links, the user running the script must have
write access to the mailbox.


RUNNING WITH REGULAR PYTHON
==========================
The script can be run with regular python2.7 if you have
"greenlet" package installed.


USES EVENTLET
=============
For fast http access, the script uses eventlet asynchronous
I/O library and it is distributed in the "eventlet" directory.
The website for eventlet is -

    http://eventlet.net


SUPPORT AND BUG REPORT
======================
Either contact us through the website:

    http://vimmaniac.com/contact-us/

Or send an email to -
    Vimmaniac Private Limited <vimmaniac@gmail.com>
    Titon Barua <titanix88@gmail.com>

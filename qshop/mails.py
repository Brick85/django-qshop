from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext as __
from qshop.qshop_settings import MAIL_TYPES


def sendMail(mail_type, variables={}, subject=None, mails=None):
    """
For each type you must create "qshop/mails/{{ mail_type }}.html" template
You can also create "qshop/mails/{{ mail_type }}_admin.html" template.
Then if "admin_mails" specified it will be used to send modified copy of mail, variables dict will be appended with "body" variable, wich constains mail body

reply_to_mail (requred)
mails
subject
subject_prefix
admin_mails
admin_subject_prefix
    """

    if not mail_type in MAIL_TYPES:
        raise 'No such mail type in list!'

    mailconf = MAIL_TYPES[mail_type]

    body = render_to_string("qshop/mails/%s.html" % mail_type, variables)

    if not mails:
        if 'mails' in mailconf:
            mails = mailconf['mails']
        else:
            raise 'No mail to send to!'
    elif isinstance(mails, basestring):
        mails = (mails,)

    if not subject:
        subject = _(mailconf['subject'])

    if 'subject_prefix' in mailconf and mailconf['subject_prefix']:
        subject = "%s%s" % (__(mailconf['subject_prefix']), subject)

    email = EmailMessage(subject, body, mailconf['reply_to_mail'], mails)
    email.content_subtype = "html"
    email.send()

    if 'admin_mails' in mailconf:
        try:
            body = render_to_string("qshop/mails/%s_admin.html" % mail_type, dict(variables.items() + {'body': body}.items()))
        except TemplateDoesNotExist:
            pass
        if 'admin_subject_prefix' in mailconf:
            subject = "%s%s" % (mailconf['admin_subject_prefix'], subject)
        email = EmailMessage(subject, body, mailconf['reply_to_mail'], mailconf['admin_mails'])
        email.content_subtype = "html"
        email.send()

import pprint
import urllib
import StringIO

from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.utils.http import urlquote
from django.http import HttpResponseRedirect
from django.conf import settings

from sitemenu.helpers import get_client_ip


if not all([hasattr(settings, elem) for elem in ['FIRSTDATA_CERT_PATH', 'FIRSTDATA_CERT_PASS']]):
    raise Exception('Project not configured to use Firstdata. You must specify variables in settings:\n\nFIRSTDATA_CERT_PATH = ""\nFIRSTDATA_CERT_PASS = ""')

try:
    import pycurl
except:
    raise Exception('Firstdata module needs pycurl.\nRun:\n    pip install pycurl')


FIRSTDATA_DEV = getattr(settings, 'FIRSTDATA_DEV', True)


class Firstdata(object):
    if FIRSTDATA_DEV:
        FIRSTDATA_ECOMM_SERVER_URL = 'https://secureshop-test.firstdata.lv:8443/ecomm/MerchantHandler'
        FIRSTDATA_ECOMM_CLIENT_URL = 'https://secureshop-test.firstdata.lv/ecomm/ClientHandler'
    else:
        FIRSTDATA_ECOMM_SERVER_URL = 'https://secureshop.firstdata.lv:8443/ecomm/MerchantHandler'
        FIRSTDATA_ECOMM_CLIENT_URL = 'https://secureshop.firstdata.lv/ecomm/ClientHandler'

    CURRENCIES = {
        'LVL': 428,
        'EUR': 978,
        'USD': 840,
        'RSD': 941,
        'SKK': 703,
        'LTL': 440,
        'EEK': 233,
        'RUB': 643,
        'YUM': 891,
    }

    def _get_currency_id(self, currency):
        if currency.upper() not in Firstdata.CURRENCIES:
            raise Exception('Wrong currency')
        return Firstdata.CURRENCIES[currency.upper()]

    def __init__(self, verbose=False):
        self.verbose = verbose

    def send_post(self, postdata):
        data = urllib.urlencode(postdata)

        curl = pycurl.Curl()
        if self.verbose:
            curl.setopt(pycurl.VERBOSE, True)
        curl.setopt(pycurl.URL, Firstdata.FIRSTDATA_ECOMM_SERVER_URL)
        curl.setopt(pycurl.HEADER, 0)
        curl.setopt(pycurl.POST, True)
        curl.setopt(pycurl.SSL_VERIFYPEER, False)
        # curl.setopt(pycurl.SSLVERSION,2)
        curl.setopt(pycurl.SSLCERT, settings.FIRSTDATA_CERT_PATH)
        curl.setopt(pycurl.CAINFO, settings.FIRSTDATA_CERT_PATH)
        curl.setopt(pycurl.SSLKEYPASSWD, settings.FIRSTDATA_CERT_PASS)
        curl.setopt(pycurl.POSTFIELDS, data)
        b = StringIO.StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.perform()

        return self.parse_answer(b.getvalue())

    def parse_answer(self, answer_data):
        lines = answer_data.split('\n')
        data = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            cols = line.split(':', 1)
            cols[0] = cols[0].upper()
            if len(cols) == 2:
                data[cols[0]] = cols[1].strip()
            else:
                data[cols[0]] = cols[0].strip()
        return data

    def start_sms_trans(self, amount, currency, ip, desc, language):
        postdata = {
            'command': 'v',
            'amount': amount,
            'currency': self._get_currency_id(currency),
            'client_ip_addr': ip,
            'description': desc,
            'language': language,
        }
        return self.send_post(postdata)

    def start_dms_auth(self, amount, currency, ip, desc, language):
        postdata = {
            'command': 'a',
            'msg_type': 'DMS',
            'amount': amount,
            'currency': self._get_currency_id(currency),
            'client_ip_addr': ip,
            'description': desc,
            'language': language,
        }
        return self.send_post(postdata)

    def make_dms_trans(self, auth_id, amount, currency, ip, desc, language):
        postdata = {
            'command': 't',
            'msg_type': 'DMS',
            'trans_id': auth_id,
            'amount': amount,
            'currency': self._get_currency_id(currency),
            'client_ip_addr': ip
        }
        return self.send_post(postdata)

    def get_trans_result(self, trans_id, ip):
        postdata = {
            'command': 'c',
            'trans_id': trans_id,
            'client_ip_addr': ip
        }
        return self.send_post(postdata)

    def reverse(self, trans_id, amount):
        postdata = {
            'command': 'r',
            'trans_id': trans_id,
            'amount': amount
        }
        return self.send_post(postdata)

    def close_day(self):
        postdata = {
            'command': 'b',
        }
        return self.send_post(postdata)


class FirstdataPayment(object):
    def get_redirect_response(self, order, request=None):
        cart = order.get_cartobject()
        currency_code = cart.get_currency().code.upper()
        total_price = "%.2f" % order.get_total_price()

        if request:
            client_ip = get_client_ip(request)
            language = request.LANGUAGE_CODE
        else:
            client_ip = '127.0.0.1'
            language = 'en'

        merchant = Firstdata(verbose=False)
        merchant_data = merchant.start_sms_trans(total_price, currency_code, client_ip, order.get_description(), language)

        if hasattr(order, 'language'):
            order.language = request.LANGUAGE_CODE

        if 'TRANSACTION_ID' in merchant_data:
            order.payment_id = merchant_data['TRANSACTION_ID']
            order.add_log_message("### payment started")
            order.save()
            return HttpResponseRedirect(Firstdata.FIRSTDATA_ECOMM_CLIENT_URL + '?trans_id=' + urlquote(merchant_data['TRANSACTION_ID']))
        else:
            order.payment_id = None
            order.paid_log = pprint.pformat(merchant_data)
            order.save()
            error_data = {
                'order_id': order.pk,
                'merchant_data': merchant_data,
            }
            mail_admins("[Django] WARNING: Firstdata payment error", pprint.pformat(error_data))
            return HttpResponseRedirect(reverse('cart_order_error'))

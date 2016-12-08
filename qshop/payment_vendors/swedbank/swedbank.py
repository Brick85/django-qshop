# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.conf import settings
from base64 import b64encode, b64decode

import ssl
import time

if not all([hasattr(settings, elem) for elem in ['SWEDBANK_VK_SND_ID', 'SWEDBANK_CERT_PATH', 'SWEDBANK_KEY_PATH']]):
    raise Exception('Project not configured to use Swedbank. You must specify variables in settings:\nSWEDBANK_VK_SND_ID, SWEDBANK_CERT_PATH, SWEDBANK_KEY_PATH')

try:
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA
    from Crypto.Util.asn1 import DerSequence
except:
    raise Exception('Swedbank module needs Crypto.\nRun:\n    pip install pycrypto')


class Swedbank(object):
    BANKLINK_URL = 'https://ib.swedbank.lv/banklink/'
    VK_SND_ID = getattr(settings, 'SWEDBANK_VK_SND_ID')
    CERT_PATH = getattr(settings, 'SWEDBANK_CERT_PATH')
    KEY_PATH = getattr(settings, 'SWEDBANK_KEY_PATH')

    def get_control_code(self, data):
        control_code = ''
        for key in self.get_controlled_params():
            control_code += u'{0:03d}{1}'.format(len(data[key]), data[key])
        return control_code

    def sign(self, data):
        key = open(Swedbank.KEY_PATH, 'r').read()
        rsakey = RSA.importKey(key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(data)
        sign = signer.sign(digest)
        return b64encode(sign)

    def verify(self, data, signature):
        public_key = self.get_public_key_from_pem(open(Swedbank.CERT_PATH, 'r').read())
        rsakey = RSA.importKey(public_key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(data.encode('utf-8'))
        if signer.verify(digest, b64decode(signature)):
            return True
        return False

    # extract public key from X.509 certificate
    # TODO: maybe manualy extract once by command: openssl x509 -pubkey -noout -in swedbank.pem > swedbank_public_key.key
    #       and save on certif dir
    def get_public_key_from_pem(self, pem_cert):
        der = ssl.PEM_cert_to_DER_cert(pem_cert)
        cert = DerSequence()
        cert.decode(der)
        tbsCertificate = DerSequence()
        tbsCertificate.decode(cert[0])
        return tbsCertificate[6]

    def pay(self):
        data = {
            'VK_SERVICE': '1002',
            'VK_VERSION': '008',
            'VK_SND_ID': Swedbank.VK_SND_ID,
            'VK_STAMP': self.payment_id,
            'VK_AMOUNT': self.amount,
            'VK_CURR': self.currency,
            'VK_REF': self.order_id,
            'VK_MSG': self.desc,
            'VK_RETURN': '{0}{1}'.format(settings.SITE_URL, reverse('payment_swedbank_return')),
            'VK_ENCODING': 'UTF-8',
            'VL_LANG': self.language,
        }
        data['VK_MAC'] = self.sign(self.get_control_code(data))

        return render_to_response('payment_vendors/swedbank/redirect_with_post.html', {
            'action': Swedbank.BANKLINK_URL,
            'form': data,
        })


class SwedbankRequest(Swedbank):
    def __init__(self, order_id, amount, currency, desc, language):
        self.order_id = str(order_id)
        self.amount = str(amount)
        self.currency = str(currency).upper()
        self.desc = desc.decode('utf-8')
        self.language = language.upper()
        self.payment_id = 'SW-{0}'.format(time.time())

    def get_controlled_params(self):
        return ['VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_STAMP', 'VK_AMOUNT', 'VK_CURR', 'VK_REF', 'VK_MSG']

    def get_payment_id(self):
        return self.payment_id


class SwedbankResponse(Swedbank):
    def __init__(self, get=None, post=None):
        if get:
            self.data = get
            self.service = get['VK_SERVICE']
        elif post:
            self.data = post
            self.service = post['VK_SERVICE']

    # VK_SERVICE: 1101: success (GET-automatic/POST-if client pressed button back to merchant)
    # VK_SERVICE: 1901: fail
    def is_paid(self):
        if self.service == '1101':
            return True
        else:
            return False

    def is_canceled(self):
        if self.service == '1901' and 'VK_AUTO' in self.data and self.data['VK_AUTO'] != 'Y':
            return True
        else:
            return False

    def get_controlled_params(self):
        if self.service == '1101':
            return ['VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_T_NO', 'VK_AMOUNT', 'VK_CURR', 'VK_REC_ACC', 'VK_REC_NAME', 'VK_SND_ACC', 'VK_SND_NAME', 'VK_REF', 'VK_MSG', 'VK_T_DATE']
        elif self.service == '1901':
            return ['VK_SERVICE', 'VK_VERSION', 'VK_SND_ID', 'VK_REC_ID', 'VK_STAMP', 'VK_REF', 'VK_MSG']

    def is_valid_response(self):
        if self.data['VK_REC_ID'] != Swedbank.VK_SND_ID:
            return False
        if not self.is_valid_signature():
            return False
        return True

    def is_valid_signature(self):
        mac = self.get_control_code(self.data)
        return self.verify(mac, self.data['VK_MAC'])

    def get_order_id(self):
        return self.data['VK_REF']

    def get_response(self):
        return self.data


class SwedbankPayment(object):
    SWEDBANK_LANGS = {
        'lv': 'LAT',
        'ru': 'RUS',
        'en': 'ENG',
    }

    def get_language(self, code):
        if code in self.SWEDBANK_LANGS:
            return self.SWEDBANK_LANGS[code]
        else:
            return 'ENG'

    def get_redirect_response(self, order, request=None):
        cart = order.get_cartobject()
        currency_code = cart.get_currency().code.upper()
        language_code = request.LANGUAGE_CODE if request else 'en'
        total_price = "%.2f" % order.get_total_price()

        swedbank = SwedbankRequest(order.pk, total_price, currency_code, order.get_description(), self.get_language(language_code))

        order.payment_id = swedbank.get_payment_id()
        order.add_log_message('### payment started')
        if hasattr(order, 'language') and request:
            order.language = request.LANGUAGE_CODE
        order.save()

        return swedbank.pay()

from .models import Currency
from django.http import HttpResponseRedirect
from sitemenu.sitemenu_settings import SERVER_CACHE_DIR

class CurrencyMiddleware(object):

    def process_request(self, request):
        get_currency = request.GET.get('currency', None)
        current_currency = None
        if get_currency:
            try:
                current_currency = Currency.objects.get(code=get_currency)
                request.session['currency'] = get_currency
                Currency.set_default_currency(current_currency)
                if SERVER_CACHE_DIR:
                    request._server_cache = {'set_cookie': True}

                return HttpResponseRedirect(request.path)
            except:
                pass
        if not current_currency:
            try:
                current_currency = Currency.objects.get(code=request.session['currency'])
            except:
                current_currency = Currency.get_default_currency()
                request.session['currency'] = current_currency.code

        Currency.current_currency = current_currency

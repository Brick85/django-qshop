from .models import Currency
from django.http import HttpResponseRedirect


class CurrencyMiddleware(object):

    def process_request(self, request):
        get_currency = request.GET.get('currency', None)
        current_currency = None
        if get_currency:
            try:
                current_currency = Currency.objects.get(code=get_currency)
                request.session['currency'] = get_currency
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

class BasePayment(object):

    def get_redirect_response(self):
        raise NotImplementedError()

    def parse_response(self, request):
        raise NotImplementedError()

class BasePayment(object):

    def get_redirect(self):
        raise NotImplementedError()

    def parse_response(self, request):
        raise NotImplementedError()

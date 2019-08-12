class BasePayment(object):

    def get_redirect_response(self, order):
        raise NotImplementedError('Method get_redirect_response not implemented!')

    def parse_response(self, request):
        raise NotImplementedError('Method parse_response not implemented!')

from qshop.qshop_settings import CART_ORDER_CUSTOM_ADMIN
if not CART_ORDER_CUSTOM_ADMIN:

    from django.contrib import admin
    from models import Order
    # from forms import OrderAdminForm

    # from psyreal.actions import export_as_csv


    class OrderAdmin(admin.ModelAdmin):
        #form = OrderAdminForm
        list_display = ('pk', '__unicode__', 'status', 'date_added')
        list_display_links = ('pk', '__unicode__')
        list_filter = ('status',)
        ordering = ['-date_added']
        readonly_fields = ('name', 'phone', 'email', 'address', 'get_cart_text', 'get_comments')
        exclude = ('comments',)

        # class Media:
        #     js = (
        #         '/static/modeltranslation/js/force_jquery.js',
        #         '/static/admin/js/order.js',
        #     )

        # def changelist_view(self, request, extra_context=None):

        #     test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
        #     if test[-1] and not test[-1].startswith('?'):
        #         if not 'payed__exact' in request.GET:
        #             q = request.GET.copy()
        #             q['payed__exact'] = '1'
        #             request.GET = q
        #             request.META['QUERY_STRING'] = request.GET.urlencode()
        #     return super(OrderAdmin, self).changelist_view(request, extra_context=extra_context)


    admin.site.register(Order, OrderAdmin)


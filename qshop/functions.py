from .models import Product, ProductToParameter
from django.http import HttpResponseRedirect
import re
from django.db.models import Q


def get_catalogue_root(menu):
    items = menu.__class__.objects.filter(pk__in=menu.get_parents_ids_list() + [menu.pk])
    for item in items:
        if item.page_type == 'pcat':
            return item
    return menu


class CategoryData:
    need_return = False
    return_data = None
    filters = {}
    products = None

    request = None
    url_add = []
    menu = None

    def __init__(self, request, url_add, menu):
        self.request = request
        self.url_add = url_add
        self.menu = menu

        self.process_filters()
        self.process_products()

    def process_products(self):
        products = Product.objects.filter(category=self.menu)

        filter_set = self.get_filter_set()

        for filter_id, filter_item in filter_set.items():
            products = products.filter(filter_item)

        self.set_aviable_filters(filter_set, products)

        for product in products:
            product._current_category = self.menu

        self.products = products

    def process_filters(self):
        filters = {}

        filters_qs = ProductToParameter.objects.select_related('parameter', 'value')\
            .filter(product__category=self.menu).exclude(value=None)\
            .order_by('parameter__parameters_set', 'parameter__order', 'value__value')
        filters_qs.query.group_by = ['value']

        for item in filters_qs:
            if not item.parameter.id in filters:
                filters[item.parameter.id] = {'name': item.parameter.name, 'values': [], 'skip_unaviable': False}
            filters[item.parameter.id]['values'].append(
                (item.value.id, {'name': item.value.value, 'active': False, 'unaviable': False})
            )

        try:
            selected_filters = self.decode_filters(self.url_add[1])
        except:
            selected_filters = {}

        if 'filteradd' in self.request.GET or 'filterdel' in self.request.GET:
            if 'filteradd' in self.request.GET:
                action_type = 'add'
                action_value = self.request.GET['filteradd']
            else:
                action_type = 'del'
                action_value = self.request.GET['filterdel']

            wrong_data = False

            try:
                f_data = re.search('f(\d+)-(\d+)', action_value)
                filter_id = int(f_data.group(1))
                filter_value = int(f_data.group(2))
            except AttributeError:
                wrong_data = True

            if not wrong_data:
                if action_type == 'add':
                    try:
                        print filter_value in selected_filters[filter_id]
                        if not filter_value in selected_filters[filter_id]:
                            selected_filters[filter_id].append(filter_value)
                    except:
                        selected_filters[filter_id] = [filter_value]
                else:
                    try:
                        selected_filters[filter_id].remove(filter_value)
                        if not selected_filters[filter_id]:
                            del selected_filters[filter_id]
                    except:
                        pass

            if not selected_filters:
                self.return_data = HttpResponseRedirect(self.menu.get_absolute_url())
            else:
                self.return_data = HttpResponseRedirect("%s%s/%s/" % (self.menu.get_absolute_url(), 'filter', self.encode_filters(selected_filters)))

            self.need_return = True
            return

        for filter_id, filter_data in filters.items():
            if filter_id in selected_filters:
                for value_id, value_data in filter_data['values']:
                    if value_id in selected_filters[filter_id]:
                        value_data['active'] = True
                        filter_data['skip_unaviable'] = True

        self.filters = filters

    def get_filter_set(self):
        filter_set = {}

        for filter_id, filter_data in self.filters.items():
            filter_arr = Q()
            for value_id, value_data in filter_data['values']:
                if value_data['active']:
                    filter_arr |= Q(producttoparameter__value_id=value_id)
            if filter_arr:
                filter_set[filter_id] = filter_arr
        return filter_set

    def set_aviable_filters(self, filter_set, products):
        aviable_parameters = ProductToParameter.objects.filter(product__in=products).distinct().values_list('value_id', flat=True)
        for filter_id, filter_data in self.filters.items():
            if not filter_data['skip_unaviable']:
                for value_id, value_data in filter_data['values']:
                    if value_id not in aviable_parameters:
                        value_data['unaviable'] = True

    def encode_filters(self, filters):
        filter_arr = []
        for k, v in filters.items():
            filter_arr.append("%s-%s" % (k, ':'.join([str(x) for x in v])))
        return '_'.join(filter_arr)

    def decode_filters(self, filters):
        filters_ret = {}
        for filter_item in filters.split('_'):
            filter_id, filter_data = filter_item.split('-', 2)
            filters_ret[int(filter_id)] = [int(x) for x in filter_data.split(':')]
        return filters_ret

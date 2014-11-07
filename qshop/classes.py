from .models import Product, ProductToParameter, ParameterValue, ParametersSet, ProductVariationValue
from django.http import Http404
from django.http import HttpResponseRedirect
import re
from django.db.models import Q
from .qshop_settings import PRODUCTS_ON_PAGE, FILTERS_ENABLED, FILTERS_NEED_COUNT, FILTERS_PRECLUDING, FILTERS_FIELDS, FILTERS_ORDER, VARIATION_FILTER_NAME, FILTER_BY_VARIATION_TYPE
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _


class CategoryData:
    need_return = False
    return_data = None
    filters = {}
    filters_order = []
    products_page = None

    request = None
    filter_string = ''
    menu = None
    sort = None
    page = 1
    default_sorting = True

    def __init__(self, request, filter_string, menu, sort, page=1, products=None):
        self.request = request
        self.filter_string = filter_string
        self.menu = menu
        self.page = page
        self.page_link = menu.get_absolute_url()
        self.init_products = products

        for i, x in enumerate(Product.SORT_VARIANTS):
            if sort == x[0]:
                self.sort = x
                if i == 0:
                    self.default_sorting = True
                else:
                    self.default_sorting = False
                break
        if not self.sort:
            raise Http404('Invalid sorting parameter')

        if not self.menu.page_type == 'pdis':
            self.process_filters()
        self.process_products()

        if self.request.get_full_path() != self.link_for_page(skip_page=False):
            self.return_data = HttpResponseRedirect(self.link_for_page(skip_page=False))
            self.need_return = True

    def process_products(self):
        if self.init_products is not None:
            products = self.init_products
        elif not self.menu.page_type == 'pdis':
            products = Product.objects.filter(category=self.menu, hidden=False)
        else:
            products = Product.objects.filter(hidden=False).exclude(discount_price=None)

        for filter_q in self.get_q_filters():
            products = products.filter(filter_q)

        if FILTERS_PRECLUDING:
            self.set_aviable_filters(products)

        if self.sort[1] == 'price' or self.sort[1] == '-price':
            sort = self.sort[1].replace('price', 'min_price')
            products = products.extra(select={'min_price': "IF(`qshop_product`.`discount_price`, `qshop_product`.`discount_price`, `qshop_product`.`price`)"}).order_by(sort)
        else:
            products = products.order_by(self.sort[1])

        products = products.distinct()

        paginator = Paginator(products, PRODUCTS_ON_PAGE)
        try:
            products_page = paginator.page(self.page)
        except (PageNotAnInteger, EmptyPage):
            raise Http404('There is no such page')

        if not self.menu.page_type == 'pdis':
            for product in products_page.object_list:
                product._current_category = self.menu

        self.products_page = products_page

    def _get_filters_data(self):
        filters = {}
        filters_order = []

        if FILTERS_ENABLED:
            for filter_key in FILTERS_ORDER:
                if filter_key == 'p':
                    filters_qs = ProductToParameter.objects.select_related('parameter', 'value')\
                        .filter(product__category=self.menu, product__hidden=False, parameter__is_filter=True).exclude(value=None)\
                        .order_by('parameter__parameters_set', 'parameter__order', 'value__value')
                    filters_qs.query.group_by = ['qshop_parametervalue.value']

                    for item in filters_qs:
                        filter_id = "p{0}".format(item.parameter.id)
                        if not filter_id in filters:
                            filters_order.append(filter_id)
                            filters[filter_id] = {'name': item.parameter.name, 'has_active': False, 'values': [], 'skip_unaviable': False, 'filter_type': 'or', 'filter_aviability_check': self._check_parameter_filter}
                        filters[filter_id]['values'].append(
                            (item.value.id, {'name': item.value.value, 'active': False, 'unaviable': False, 'count': 0, 'filter': Q(producttoparameter__value_id=item.value.id)})
                        )
                elif filter_key == 'v':
                    variations = ProductVariationValue.objects.filter(productvariation__product__category=self.menu, productvariation__product__hidden=False).distinct().order_by('value')
                    if variations:
                        filters_order.append('v')

                        if hasattr(self.menu, 'get_variation_name'):
                            variation_name = self.menu.get_variation_name()
                        elif hasattr(ParametersSet, 'get_variation_name'):
                            try:
                                variation_name = ParametersSet.objects.filter(product__category=self.menu)[0].get_variation_name()
                            except:
                                variation_name = _(VARIATION_FILTER_NAME)
                        else:
                            variation_name = _(VARIATION_FILTER_NAME)

                        filters['v'] = {'name': variation_name, 'has_active': False, 'values': [], 'skip_unaviable': False, 'filter_type': FILTER_BY_VARIATION_TYPE, 'filter_aviability_check': self._check_variation_filter}
                        for variation in variations:
                            filters['v']['values'].append(
                                (variation.id, {'name': variation.get_filter_name(), 'active': False, 'unaviable': False, 'count': 0, 'filter': Q(productvariation__variation_id=variation.id)})
                            )
                else:
                    field_name = FILTERS_FIELDS[filter_key]
                    if not hasattr(Product, field_name):
                        raise Exception('[qShop exception] Filter configuration error: there is no {0} in Product class!'.format(field_name))
                    field = Product._meta.get_field_by_name(field_name)[0]
                    model = field.rel.to
                    items = model.objects.filter(product__category=self.menu, product__hidden=False).distinct()
                    if items:
                        filters_order.append(filter_key)
                        filters[filter_key] = {'name': field.verbose_name, 'has_active': False, 'values': [], 'skip_unaviable': False, 'filter_type': 'or', 'filter_aviability_check': self._check_foreignkey_filter}
                        for item in items:
                            q = {
                                '{0}_id'.format(field_name): item.id
                            }
                            filters[filter_key]['values'].append(
                                (item.id, {'name': item.__unicode__(), 'active': False, 'unaviable': False, 'count': 0, 'filter': Q(**q)})
                            )

        return filters, filters_order

    def process_filters(self):
        filters, filters_order = self._get_filters_data()

        if FILTERS_ENABLED:
            try:
                selected_filters = self.decode_filters(self.filter_string)
            except:
                selected_filters = {}

            if 'filteradd' in self.request.GET or 'filterdel' in self.request.GET or 'filterset' in self.request.GET or 'filterclear' in self.request.GET:
                if 'filteradd' in self.request.GET:
                    action_type = 'add'
                    action_value = self.request.GET['filteradd']
                elif 'filterdel' in self.request.GET:
                    action_type = 'del'
                    action_value = self.request.GET['filterdel']
                elif 'filterset' in self.request.GET:
                    action_type = 'set'
                    action_value = self.request.GET['filterset']
                else:
                    action_type = 'clear'
                    action_value = ''

                wrong_data = False

                try:
                    f_data = re.search('f([\d\w]+)-(\d+)', action_value)
                    filter_id = str(f_data.group(1))
                    filter_value = int(f_data.group(2))
                except AttributeError:
                    wrong_data = True

                if not wrong_data:
                    if action_type == 'add':
                        try:
                            if not filter_value in selected_filters[filter_id]:
                                selected_filters[filter_id].append(filter_value)
                        except:
                            selected_filters[filter_id] = [filter_value]
                    elif action_type == 'del':
                        try:
                            selected_filters[filter_id].remove(filter_value)
                            if not selected_filters[filter_id]:
                                del selected_filters[filter_id]
                        except:
                            pass
                    elif action_type == 'set':
                        selected_filters[filter_id] = [filter_value]
                elif 'filterclear' in self.request.GET:
                    selected_filters = {}

                if not selected_filters:
                    self.filter_string = ''
                else:
                    self.filter_string = self.encode_filters(selected_filters)

                self.return_data = HttpResponseRedirect(self.link_for_page(skip_page=True))

                self.need_return = True
                return

            for filter_id, filter_data in filters.items():
                if filter_id in selected_filters:
                    for value_id, value_data in filter_data['values']:
                        if value_id in selected_filters[filter_id]:
                            value_data['active'] = True
                            filter_data['skip_unaviable'] = True
                            filter_data['has_active'] = True

        self.filters = filters
        self.filters_order = filters_order

    def get_q_filters(self):
        filters_q = []

        if FILTERS_ENABLED:
            for filter_id, filter_data in self.filters.items():
                filter_arr = Q()
                for value_id, value_data in filter_data['values']:
                    if value_data['active']:
                        if filter_data['filter_type'] == 'or':
                            filter_arr |= value_data['filter']
                        else:
                            filters_q.append(value_data['filter'])
                if filter_arr:
                    filters_q.append(filter_arr)
        return filters_q

    def set_aviable_filters(self, products):
        if FILTERS_ENABLED:
            for filter_id, filter_data in self.filters.items():
                if hasattr(filter_data['filter_aviability_check'], '__call__'):
                    filter_data['filter_aviability_check'](filter_id, filter_data, products)

    def encode_filters(self, filters):
        filter_arr = []
        for k, v in filters.items():
            filter_arr.append("%s-%s" % (k, ':'.join(sorted([str(x) for x in v]))))
        return '_'.join(filter_arr)

    def decode_filters(self, filters):
        filters_ret = {}
        for filter_item in filters.split('_'):
            filter_id, filter_data = filter_item.split('-', 2)
            filters_ret[str(filter_id)] = [int(x) for x in filter_data.split(':')]
        return filters_ret

    def link_for_page(self, sorting=None, skip_page=True):
        string = ''
        if not sorting and not self.default_sorting:
            string += 'sort-%s/' % self.sort[0]
        if sorting and (sorting != Product.SORT_VARIANTS[0][0]):
            string += 'sort-%s/' % sorting
        if self.filter_string:
            string += 'filter-%s/' % self.filter_string
        if not skip_page and int(self.page) != 1:
            string += 'page-%s/' % self.page

        return self.menu.get_absolute_url() + string

    def get_sorting_variants(self):
        for variant in Product.SORT_VARIANTS:
            try:
                add = variant[3]
            except IndexError:
                add = None
            yield {
                'link': self.link_for_page(sorting=variant[0], skip_page=True),
                'name': variant[2],
                'selected': True if variant[0] == self.sort[0] else False,
                'add': add
            }

    def get_sorting_variants_as_list(self):
        return list(self.get_sorting_variants())

    def get_filters(self):
        for item in self.filters_order:
            yield (item, self.filters[item])

    def _check_parameter_filter(self, filter_id, filter_data, products):
        if not hasattr(self, '_check_parameter_filter_aviable_parameters'):
            if FILTERS_NEED_COUNT:
                aviable_parameters_data = ParameterValue.objects.filter(producttoparameter__product__in=products).annotate(total_items=Count('id')).values_list('id', 'total_items')
                aviable_parameters = []
                parameters_counts = {}
                for aviable_parameter, parameter_count in aviable_parameters_data:
                    aviable_parameters.append(aviable_parameter)
                    parameters_counts[aviable_parameter] = parameter_count
            else:
                aviable_parameters = ProductToParameter.objects.filter(product__in=products).distinct().values_list('value_id', flat=True)
                parameters_counts = {}
            self._check_parameter_filter_aviable_parameters = aviable_parameters
            self._check_parameter_filter_parameters_counts = parameters_counts

        aviable_parameters = self._check_parameter_filter_aviable_parameters
        parameters_counts = self._check_parameter_filter_parameters_counts

        for value_id, value_data in filter_data['values']:
            if FILTERS_NEED_COUNT and value_id in parameters_counts:
                value_data['count'] = parameters_counts[value_id]
            if value_id not in aviable_parameters:
                if not filter_data['skip_unaviable']:
                    value_data['unaviable'] = True

    def _check_variation_filter(self, filter_id, filter_data, products):
        if FILTERS_NEED_COUNT:
            aviable_variations_data = ProductVariationValue.objects.filter(productvariation__product__in=products).annotate(total_items=Count('id')).values_list('id', 'total_items')
            aviable_variations = []
            variations_counts = {}
            for aviable_parameter, parameter_count in aviable_variations_data:
                aviable_variations.append(aviable_parameter)
                variations_counts[aviable_parameter] = parameter_count
        else:
            aviable_variations = ProductVariationValue.objects.filter(productvariation__product__in=products).distinct().values_list('id', flat=True)
            variations_counts = {}

        for value_id, value_data in filter_data['values']:
            if FILTERS_NEED_COUNT and value_id in variations_counts:
                value_data['count'] = variations_counts[value_id]
            if value_id not in aviable_variations:
                if not filter_data['skip_unaviable']:
                    value_data['unaviable'] = True

    def _check_foreignkey_filter(self, filter_id, filter_data, products):
        field_name = FILTERS_FIELDS[filter_id]
        field = Product._meta.get_field_by_name(field_name)[0]
        model = field.rel.to

        model.objects.filter(product__category=self.menu).distinct()

        if FILTERS_NEED_COUNT:
            aviable_field_data = model.objects.filter(product__in=products).annotate(total_items=Count('id')).values_list('id', 'total_items')
            aviable_field = []
            field_counts = {}
            for item, count in aviable_field_data:
                aviable_field.append(item)
                field_counts[item] = count
        else:
            aviable_field = model.objects.filter(product__in=products).distinct().values_list('id', flat=True)
            field_counts = {}

        for value_id, value_data in filter_data['values']:
            if FILTERS_NEED_COUNT and value_id in field_counts:
                value_data['count'] = field_counts[value_id]
            if value_id not in aviable_field:
                if not filter_data['skip_unaviable']:
                    value_data['unaviable'] = True

from django.forms import formsets, ModelForm
from django.forms.models import BaseInlineFormSet
from .models import ProductToTypeField



class ProductToTypeFieldForm(ModelForm):
    class Meta:
        model = ProductToTypeField

class BaseProductToTypeFieldFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        data = {}
        for item in ProductToTypeField.objects.filter(product=kwargs['instance']):
            data[item.type_field.id] = item

        self.__initial = []
        if not kwargs['instance'].skip_init_type_fields():
            for item in kwargs['instance'].product_specs_type.producttypefield_set.all():
                init = {}
                init['initial'] = {'type_field': item.id}
                try:
                    init['initial']['value']    = data[item.id].value
                    init['instance'] = data[item.id]
                except:
                    init['initial']['value'] = ''
                self.__initial.append(init)
        super(BaseProductToTypeFieldFormset, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return ProductToTypeField.objects.filter(product=-1)

    def total_form_count(self):
        return len(self.__initial) + self.extra

    def _construct_forms(self):
        self.forms = []
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i))

    def _construct_form(self, i, **kwargs):
        if self.__initial:
            try:
                kwargs['instance'] = self.__initial[i]['instance']
                kwargs['empty_permitted'] = False
            except:
                try:
                    kwargs['initial'] = self.__initial[i]['initial']
                    kwargs['empty_permitted'] = True
                except IndexError:
                    pass
        return formsets.BaseFormSet._construct_form(self, i, **kwargs)


ProductToTypeFieldFormset = formsets.formset_factory(ProductToTypeFieldForm, formset=BaseProductToTypeFieldFormset)

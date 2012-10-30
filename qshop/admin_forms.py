from django.forms.models import BaseInlineFormSet
from .models import ParameterValue, Parameter


class ProductToParameterFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(ProductToParameterFormset, self).add_fields(form, index)
        values = ParameterValue.objects.none()
        if form.instance:
            try:
                parameter = form.instance.parameter
            except Parameter.DoesNotExist:
                pass
            else:
                values = ParameterValue.objects.filter(parameter=parameter)
        form.fields['value'].queryset = values

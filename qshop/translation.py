from modeltranslation.translator import translator, TranslationOptions
from qshop.models import Product, ProductVariationValue, ProductVariation, ProductImage, ParametersSet, Parameter, ParameterValue, ProductToParameter

for model in Product, ProductVariationValue, ProductVariation, ProductImage, ParametersSet, Parameter, ParameterValue, ProductToParameter:
    if hasattr(model, '_translation_fields'):
        translation_option = type("{0}Translation".format(model.__name__), (TranslationOptions,), {
            'fields': model._translation_fields,
        })
        translator.register(model, translation_option)

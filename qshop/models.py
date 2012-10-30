from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item

Menu = import_item(MENUCLASS)


class Product(models.Model):
    SORT_VARIANTS = (
        ('price_asc', 'price', _('price low to high')),
        ('price_desc', '-price', _('price high to low')),
        ('name', 'name', _('by name')),
    )

    has_variations = models.BooleanField(default=False, editable=False)
    parameters_set = models.ForeignKey('ParametersSet', verbose_name=_('parameters set'))
    articul = models.SlugField(_('articul'))
    name    = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2)
    description = models.TextField(_('description'), default='', blank=True)
    image = ThumbnailerImageField(_('image'), upload_to='products/main', blank=True, resize_source=dict(size=(1024, 1024)))

    category = models.ManyToManyField(Menu, verbose_name=_('category'))

    parameters = models.ManyToManyField('Parameter', through='ProductToParameter', verbose_name=_('parameters'))

    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['order']

    def __unicode__(self):
        return "%s (articul: %s)" % (self.name, self.articul)

    def get_absolute_url(self):
        try:
            return self.absolute_url
        except:
            category = self.get_current_category()
            self.absolute_url = reverse('dispatcher', kwargs={'url': "%s%s/" % (category.full_url, self.articul)})
            return self.absolute_url

    def get_current_category(self):
        try:
            return self._current_category
        except:
            self._current_category = self.category.all()[0]
            return self._current_category

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.old_parameters_set_id = self.parameters_set_id

    # def save(self, skip_variations=False, *args, **kwargs):
    #     super(Product, self).save(*args, **kwargs)

    def has_parameters(self):
        if self._get_parameters_for_product():
            return True
        return False

    def get_parameters(self):
        try:
            return self._parameters_list
        except:
            pass

        ret = []
        for item in self._get_parameters_for_product():
            ret.append({
                'id': item.value_id,
                'name': item.parameter.name,
                'value': item.value.value
            })

        self._parameters_list = ret
        return self._parameters_list

    def _get_parameters_for_product(self):
        try:
            return self._parameters_for_product
        except:
            self._parameters_for_product = ProductToParameter.objects.select_related('parameter', 'value').filter(product=self).exclude(value=None)
            return self._parameters_for_product

    def get_additional_images(self):
        try:
            return self._additional_images
        except:
            self._additional_images = self.productimage_set.all()
        return self._additional_images

    def is_parametrs_set_changed(self):
        if self.old_parameters_set_id != self.parameters_set_id:
            return True
        return False

    def get_variations(self):
        try:
            return self._get_variations
        except:
            self._get_variations = self.productvariation_set.all()
            return self._get_variations

    def get_price(self):
        return self.price

    def get_price_formatted(self):
        return self.get_price()


class ProductVariationValue(models.Model):
    value = models.CharField(_('name'))

    def __unicode__(self):
        return "%s" % self.value


class ProductVariation(models.Model):
    product = models.ForeignKey(Product)
    variation = models.ForeignKey(ProductVariationValue)
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = _('product variation')
        verbose_name_plural = _('product variations')

    def save(self, skip_variations=False, *args, **kwargs):
        super(ProductVariation, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.name

    def get_price(self):
        return self.price

    def get_price_formatted(self):
        return self.get_price()


class ProductImage(models.Model):
    image = ThumbnailerImageField(_('image'), upload_to='products/more', resize_source=dict(size=(1024, 1024)))
    product = models.ForeignKey(Product)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    def __unicode__(self):
        return "%s" % self.image


class ParametersSet(models.Model):
    name = models.CharField(_('name'), max_length=64)

    def __unicode__(self):
        return self.name


class Parameter(models.Model):
    parameters_set = models.ForeignKey(ParametersSet)
    name = models.CharField(_('name'), max_length=128)
    is_filter = models.BooleanField(_('is filter'), default=True)
    order = models.IntegerField(_('order'))

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.name


class ParameterValue(models.Model):
    parameter = models.ForeignKey(Parameter)
    value = models.CharField(_('parameter value'), max_length=128)

    class Meta:
        unique_together = (("parameter", "value"),)

    def __unicode__(self):
        return self.value


class ProductToParameter(models.Model):
    product = models.ForeignKey(Product)
    parameter = models.ForeignKey(Parameter)
    value = models.ForeignKey(ParameterValue, blank=True, null=True)

    def __unicode__(self):
        return 'Product Field Nr. %d' % self.parameter_id

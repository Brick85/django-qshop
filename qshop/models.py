from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item

Menu = import_item(MENUCLASS)


class Product(models.Model):
    # has_variations = models.BooleanField(default=False) #editable=False,
    product_specs_type = models.ForeignKey('ProductType', verbose_name=_('product type'))
    articul = models.SlugField(_('articul'))
    name    = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=5, decimal_places=2)
    description = models.TextField(_('description'), default='', blank=True)
    image = ThumbnailerImageField(_('image'), upload_to='products/main', blank=True, resize_source=dict(size=(1024, 1024)))

    category = models.ManyToManyField(Menu, verbose_name=_('category'))

    specs = models.ManyToManyField('ProductTypeField', through='ProductToTypeField', verbose_name=_('specifications'))

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
        self.old_product_specs_type_id = self.product_specs_type_id

    def save(self, skip_variations=False, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)

    def has_specs(self):
        if self._get_specs_for_product():
            return True
        return False

    def get_specs(self):
        try:
            return self._specs_list
        except:
            pass
        product_data = {}
        for item in self._get_specs_for_product():
            product_data[item.type_field.id] = item

        ret = []
        for item in self.product_specs_type.producttypefield_set.all():
            try:
                value = product_data[item.id].value
            except:
                value = item.default_value
            if value == '':
                value = item.default_value

            if value != '':
                ret.append({
                    'name': item.name,
                    'value': value
                })
        self._specs_list = ret
        return ret

    def _get_specs_for_product(self):
        try:
            return self._specs_for_product
        except:
            self._specs_for_product = ProductToTypeField.objects.filter(product=self)
            return self._specs_for_product

    def get_additional_images(self):
        try:
            return self._additional_images
        except:
            self._additional_images = self.productimage_set.all()
        return self._additional_images

    def skip_init_type_fields(self):
        if not self.pk:
            return True
        if self.old_product_specs_type_id != self.product_specs_type_id:
            return True
        return False

    def get_value_for_spec(self, spec):
        try:
            product_data = self._specs
        except:
            product_data = {}
            for item in ProductToTypeField.objects.filter(product=self):
                product_data[item.type_field.id] = item
            self._specs = product_data
        try:
            ret = product_data[spec.id].value
        except:
            ret = spec.value
        if ret == '':
            ret = _('n/a')

        return ret


class ProductVariation(models.Model):
    product = models.ForeignKey(Product)
    name = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = _('product variation')
        verbose_name_plural = _('product variations')

    def save(self, skip_variations=False, *args, **kwargs):
        super(ProductVariation, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.name


class ProductImage(models.Model):
    image = ThumbnailerImageField(_('image'), upload_to='products/more', resize_source=dict(size=(1024, 1024)))
    product = models.ForeignKey(Product)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    def __unicode__(self):
        return "%s" % self.image


class ProductType(models.Model):
    name = models.CharField(_('name'), max_length=64)

    def __unicode__(self):
        return self.name


class ProductTypeField(models.Model):
    product_type = models.ForeignKey(ProductType)
    name = models.CharField(_('name'), max_length=128)
    default_value = models.CharField(_('default value'), max_length=256, blank=True)
    order = models.IntegerField(_('order'))

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.name


class ProductToTypeField(models.Model):
    product = models.ForeignKey(Product)
    type_field = models.ForeignKey(ProductTypeField)
    value = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return 'Product Field Nr. %d' % self.type_field.id

    def save(self, *args, **kwargs):
        super(ProductToTypeField, self).save(*args, **kwargs)

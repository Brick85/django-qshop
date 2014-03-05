#!/usr/bin/env python
from setuptools import setup

setup(name='django-qshop',
      version='0.1.2',
      description='E-commerce for django. Requires django-sitemenu. Alpha version.',
      long_description='E-commerce for django. Requires django-sitemenu. Alpha version.',
      author='Vital Belikov',
      author_email='vital@qwe.lv',
      packages=['qshop', 'qshop.templatetags', 'qshop.cart'],
      url='https://github.com/Brick85/django-qshop',
      include_package_data=True,
      zip_safe=False,
      requires=['django(>=1.4)', 'django_sitemenu', 'easy_thumbnails'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Utilities'],
      license='New BSD')

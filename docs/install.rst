============
Installation
============

You can install django-qshop from GitHub_ or from PyPI_: ::

    pip install django-qshop

.. _GitHub: https://github.com/Brick85/django-qshop
.. _PyPI: http://pypi.python.org/pypi/django-qshop


Add to INSTALLED_APPS: ::

    INSTALLED_APPS = (
        ...
        'sitemenu',
        'qshop',
        'qshop.cart',
        'easy_thumbnails',
        ...
    )

And add to urls.py: ::

    url(r'^cart/', include('qshop.cart.urls')),



Requirements
============

* Django 1.4+
* `django-sitemenu`_
* easy_thumbnails

.. _django-sitemenu: https://github.com/Brick85/sitemenu

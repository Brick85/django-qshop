============
Installation
============

You can install django-qshop from GitHub_

.. _GitHub: https://github.com/Brick85/django-qshop

Or from PyPI: ::

    pip install django-qshop

And add to INSTALLED_APPS: ::

    INSTALLED_APPS = (
        ...
        'sitemenu',
        'qshop',
        'qshop.cart',
        'easy_thumbnails',
        ...
    )


Requirements
============

* Django 1.4+
* `django-sitemenu`_
* easy_thumbnails

.. _django-sitemenu: https://github.com/Brick85/sitemenu

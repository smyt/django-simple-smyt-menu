"""Simple menu app tests."""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
try:
    from unittest import mock
except:
    import mock
from django.test import TestCase, RequestFactory
from django.template import Context, Template
from django.conf.urls import url
from django.test.utils import override_settings

from menu.models import Menu, Item


urlpatterns = [
    url(r'^$', mock.Mock(), name='index'),
    url(r'^i2$', mock.Mock(), name='i2'),
    url(r'^i3$', mock.Mock(), name='i3'),
    url(r'^i4$', mock.Mock(), name='i4'),
    url(r'^i41$', mock.Mock(), name='i41'),
    url(r'^i5$', mock.Mock(), name='i5'),
]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@override_settings(ROOT_URLCONF=__name__)
class MenuTestCase(TestCase):
    """Menu tags testcase."""

    def setUp(self):
        """Create menus and menu items."""
        self.factory = RequestFactory()
        menu1 = Menu.objects.create(name='main', depth=5)
        menu2 = Menu.objects.create(name='second')
        Item.objects.bulk_create([
            Item(id=1, menu=menu1, name='Index', url='index'),
            Item(id=2, menu=menu1, name='I2', url='/i2', parent_id=1),
            Item(id=22, menu=menu1, name='I22', url='/i22', parent_id=1),
            Item(id=3, menu=menu1, name='I3', url='/i3', parent_id=2),
            Item(id=4, menu=menu1, name='I4', url='/i4', parent_id=3),
            Item(id=41, menu=menu1, name='I41', url='i41', parent_id=3),
            Item(id=32, menu=menu1, name='I32', url='/i32', parent_id=2),
            Item(id=42, menu=menu1, name='I42', url='/i42', parent_id=32),
            Item(id=5, menu=menu1, name='I5', url='/i5', parent_id=4),
            Item(id=52, menu=menu1, name='I52', url='/i52', parent_id=4),
            Item(id=6, menu=menu1, name='Another Root Item', url='/another_root'),
            Item(id=7, menu=menu1, name='Another Root Item2', url='/another_root_2'),
            Item(id=62, menu=menu1, name='I62', url='/i62', parent_id=6),
            Item(id=8, menu=menu2, name='I8', url='/i8'),
        ])

    def check_menu(self, template):
        """Test results for both tags."""
        request = self.factory.get('/i3')
        c = Context({"request": request})
        rendered_page = template.render(c)

        # Current item is I3
        self.assertInHTML('<li class="current">I3</li>', rendered_page)

        # Neighbours are shown
        self.assertInHTML('<li class="neighbour"><a href="/i32">I32</a></li>', rendered_page)
        self.assertInHTML('<li class="neighbour"><a href="/i22">I22</a></li>', rendered_page)

        # Root parent item has class 'selected'. Also it saved with url name, not path
        self.assertInHTML('<li class="selected"><a href="/">Index</a></li>', rendered_page)

        # All other root items has class 'root'
        self.assertInHTML('<li class="root"><a href="/another_root">Another Root Item</a></li>', rendered_page)
        self.assertInHTML('<li class="root"><a href="/another_root_2">Another Root Item2</a></li>', rendered_page)

        # Check child
        self.assertInHTML('<li class="child"><a href="/i4">I4</a></li>', rendered_page)
        self.assertInHTML('<li class="child"><a href="/i41">I41</a></li>', rendered_page)

        # I5 is not included - it's too far
        self.assertNotIn('I5', rendered_page)
        self.assertNotIn('I52', rendered_page)

        # I62 is not included - it has wrong parent
        self.assertNotIn('I62', rendered_page)

        # I8 is not included - it has wrong menu
        self.assertNotIn('I8', rendered_page)

    def check_last_menu_item(self, template):
        """Test results for both tags."""
        request = self.factory.get('/i5')
        c = Context({"request": request})
        rendered_page = template.render(c)

        # Current item is I5
        self.assertInHTML('<li class="current">I5</li>', rendered_page)
        self.assertInHTML('<li class="neighbour"><a href="/i52">I52</a></li>', rendered_page)

    def test_sql_menu(self):
        """Test sql menu tag."""
        t = Template('{% load menus %}{% draw_sql_menu "main" %}')
        self.check_menu(t)
        self.check_last_menu_item(t)

    def test_orm_menu(self):
        """Test orm menu tag."""
        t = Template('{% load menus %}{% draw_orm_menu "main" %}')
        self.check_menu(t)
        self.check_last_menu_item(t)

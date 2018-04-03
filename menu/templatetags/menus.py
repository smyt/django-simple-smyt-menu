# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
try:
    logging = settings.LOGGER
except AttributeError:
    import logging
from itertools import groupby

from django import template
from django.urls import reverse
from django.db.models import Q
from django.core.urlresolvers import resolve

from django.urls.exceptions import NoReverseMatch

from menu.models import Item
from menu.models import Menu


register = template.Library()


@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    '''Tag for menu drawing

    Parameters
    ----------
    menu_name : str
        Menu's name (menu.models.Menu.name).

    Returns
    -------
    dict
        Example:
            {
             # Menu instance
             u'menu': <Menu: main>,

             # Menu items
             u'levels': [[{'menu_id': 2,
                           'name': u'Main Another',
                           'url': u'/56',
                           'class': u'',  # class for css
                           'id': 7,
                           'parent_id': None,
                           'order': 0},
                          {'menu_id': 2,
                           'name': u'Main and Parent',
                           'url': u'/',
                           'class': u'selected',  # class for parent items
                           'id': 4,
                           'parent_id': None,
                           'order': 1}],

                         [{'menu_id': 2,
                           'name': u'Neighbour 2 level',
                           'url': u'/t',
                           'class': u'',
                           'id': 10,
                           'parent_id': 4,
                           'order': 0},
                          {'menu_id': 2,
                           'name': u'2 level',
                           'url': u'/i2',
                           'class': u'current',  # class for current page
                           'id': 12,
                           'parent_id': 4,
                           'order': 0}],

                         [{'menu_id': 2,
                           'name': u'THIS PAGE',
                           'url': u'/i3',
                           'class': u'',
                           'id': 5,
                           'parent_id': 12,
                           'order': 0}]]}
    '''

    request = context['request']
    current_path = request.path_info
    current_url_name = resolve(current_path).url_name

    try:
        # We need depth for query filter
        # If move depth to settings or hardcode it - get 1 query for draw_menu
        menu = Menu.objects.get(name=menu_name)
    except Menu.DoesNotExist:
        logging.error('Menu with name "{}" not found'.format(menu_name))
        return None

    menu_items = Item.objects.filter(menu__name=menu.name)
    items = menu_items.filter(Q(url=current_url_name) | Q(url=current_path))

    i = 0
    filter_prefix = 'parent__'

    # initial filter includes root items and current item's children
    tree_filter = Q(parent__isnull=True) | Q(parent__in=items.values('id'))

    # Build filter for inner items
    # 2 levels are root and child items from tree_filter
    while i <= menu.depth - 2:
        filter_value = '{}parent_id'.format(i * filter_prefix)
        tree_filter = tree_filter | \
            Q(**({'parent__in': items.values(filter_value)}))
        i += 1

    # get from DB
    items = menu_items.filter(tree_filter).distinct() \
        .order_by('parent_id', 'order').values()

    result_menu = []
    if items:
        # Group items by parent
        menu_data = groupby(items, key=lambda x: x['parent_id'])

        # save menu to dict for later using
        dict_menu = dict()
        for parent, menu_level in menu_data:
            dict_menu[parent] = list(menu_level)

        def get_children(node):
            ''' build result list for menu, check URLs, add classes'''
            current_level = dict_menu.get(node)

            for item in current_level:

                if '/' not in item['url']:
                    try:
                        item['url'] = reverse(item['url'])
                    except NoReverseMatch:
                        item['url'] = '#'

                item['class'] = ''
                if dict_menu.get(item['id']):
                    item['class'] = 'selected'
                    get_children(item['id'])

                if item['url'] == current_url_name or \
                        item['url'] == current_path:
                    item['class'] = 'current'

            result_menu.append(current_level)

        get_children(None)
        result_menu.reverse()
    else:
        logging.error('menu with name "{}" is empty'.format(menu_name))

    return {'levels': result_menu, 'menu': menu}

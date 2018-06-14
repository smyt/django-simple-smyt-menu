# -*- coding: utf-8 -*-
"""Template tags for menu drawing."""
from __future__ import unicode_literals

from django.conf import settings
try:
    logging = settings.LOGGER
except AttributeError:
    import logging
from itertools import groupby

from django import template
from django.urls import reverse, resolve
from django.db.models import Q

from django.urls.exceptions import NoReverseMatch

from menu.models import Item
from menu.models import Menu


register = template.Library()


@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_sql_menu(context, menu_name):
    """Tag for menu drawing with SQL.

    Parameters
    ----------
    menu_name : str
        Menu's name (menu.models.Menu.name).

    Returns
    -------
    dict
        Example:
            {
             # Menu name
             'menu_name': 'name',

             # Menu items
             {'levels': [
                         # Root level
                         [{'name': 'Index',
                           'parent_id': None,
                           'url': '/',
                           'class': 'selected',
                           'id': 1,
                           'menu_id': 1,
                           'order': 0,
                           'level': -2,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f26741d0>},
                          {'name': 'Another Root Item',
                           'parent_id': None,
                           'url': '/another_root',
                           'class': 'root',
                           'id': 6,
                           'menu_id': 1,
                           'order': 0,
                           'level': -2,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f26747b8>},
                          {'name': 'Another Root Item2',
                           'parent_id': None,
                           'url': '/another_root_2',
                           'class': 'root',
                           'id': 7,
                           'menu_id': 1,
                           'order': 0,
                           'level': -2,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f2674a58>}],
                         # 2 level
                         [{'name': 'I2',
                           'parent_id': 1,
                           'url': '/i2',
                           'class': 'selected',
                           'id': 2,
                           'menu_id': 1,
                           'order': 0,
                           'level': -1,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f26749b0>},
                          {'name': 'I22',
                           'parent_id': 1,
                           'url': '/i22',
                           'class': 'neighbour',
                           'id': 22,
                           'menu_id': 1,
                           'order': 0,
                           'level': -1,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f26748d0>}],
                         # Current level
                         [{'name': 'I3',
                           'parent_id': 2,
                           'url': '/i3',
                           'class': 'current',
                           'id': 3,
                           'menu_id': 1,
                           'order': 0,
                           'level': 0,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f26749e8>},
                          {'name': 'I32',
                           'parent_id': 2,
                           'url': '/i32',
                           'class': 'neighbour',
                           'id': 32,
                           'menu_id': 1,
                           'order': 0,
                           'level': 0,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f2674f98>}],
                         # Child level
                         [{'name': 'I4',
                           'parent_id': 3,
                           'url': '/i4',
                           'class': 'child',
                           'id': 4,
                           'menu_id': 1,
                           'order': 0,
                           'level': 1,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f2674c88>},
                          {'name': 'I41',
                           'parent_id': 3,
                           'url': '/i41',
                           'class': 'child',
                           'id': 41,
                           'menu_id': 1,
                           'order': 0,
                           'level': 1,
                           '_state': <django.db.models.base.ModelState object at 0x7f59f2674cc0>}]]}
    """
    request = context['request']
    current_path = request.path_info
    current_url_name = resolve(current_path).url_name

    sql_query = """
        --build tree items from selected item up to root
        WITH
            current_item AS
                  (SELECT menu_item.*, 0 AS level, CAST('current' AS text) AS class
                   FROM menu_item
                   INNER JOIN menu_menu ON menu_item.menu_id=menu_menu.id
                   WHERE menu_menu.name=%s
                     AND (menu_item.url=%s
                          OR menu_item.url=%s)),
             menu_tree AS
                  (WITH RECURSIVE tree AS
                     (SELECT * FROM current_item
                      UNION
                      SELECT menu_item.*, tree.level - 1 AS level, 'selected' AS class FROM menu_item
                      INNER JOIN tree ON menu_item.id=tree.parent_id)
                   SELECT * FROM tree )

        SELECT * FROM menu_tree

        --current item's children
        UNION
            SELECT menu_item.*, 1 AS level, 'child' AS class
                FROM menu_item
                WHERE menu_item.parent_id=(SELECT id from current_item)

        --all root items except current item's parent
        UNION
            SELECT menu_item.*, (SELECT MIN(level) from menu_tree) AS level, 'root' AS class
                FROM menu_item
                INNER JOIN menu_menu ON menu_menu.id=menu_item.menu_id
                WHERE menu_menu.name=%s AND menu_item.parent_id IS NULL
                    AND menu_item.id NOT IN (SELECT id FROM menu_tree)
        --parent neighbours
        UNION
            SELECT menu_item.*, menu_tree.level + 1 AS level, 'neighbour' AS class
                FROM menu_item, menu_tree
                WHERE menu_item.parent_id=menu_tree.id
                    AND menu_item.id NOT IN (SELECT id FROM menu_tree)
                    AND menu_item.parent_id != (SELECT id FROM current_item)
        ORDER BY level, \"order\"
        """

    result_menu = []
    items = Item.objects.raw(sql_query,
                             params=[menu_name,
                                     current_path,
                                     current_url_name,
                                     menu_name])

    # RawQuerySet has no methods for non-empty check
    try:
        items = [i for i in items]
    except TypeError:
        pass
    else:
        for key, level in groupby(items, key=lambda x: x.level):
            level_menu = []
            for item in level:
                if '/' not in item.url:
                    try:
                        item.url = reverse(item.url)
                    except NoReverseMatch:
                        item.url = '#'
                level_menu.append(item.__dict__)
            result_menu.append(level_menu)
    finally:
        return {'levels': result_menu, 'menu_name': menu_name}


@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_orm_menu(context, menu_name):
    """Tag for menu drawing with Django ORM only.

    Parameters
    ----------
    menu_name : str
        Menu's name (menu.models.Menu.name).

    Returns
    -------
    dict
        Example:
            {
             # Menu name for id
             u'menu_name': u'main',

             # Menu items
             u'levels': [
                         # Root level
                         [{'menu_id': 1,
                           'name': u'Index',
                           'url': u'/',
                           'class': u'selected',
                           'id': 1,
                           'parent_id': None,
                           'order': 0},
                          {'menu_id': 1,
                           'name': u'Another Root Item',
                           'url': u'/another_root',
                           'class': u'root',
                           'id': 6,
                           'parent_id': None,
                           'order': 0},
                          {'menu_id': 1,
                           'name': 'Another Root Item2',
                           'url': '/another_root_2',
                           'class': 'root',
                           'id': 7,
                           'parent_id': None,
                           'order': 0}],
                         # 2 level
                         [{'menu_id': 1,
                           'name': 'I2',
                           'url': '/i2',
                           'class': 'selected',
                           'id': 2,
                           'parent_id': 1,
                           'order': 0},
                          {'menu_id': 1,
                           'name': 'I22',
                           'url': '/i22',
                           'class': 'neighbour',
                           'id': 22,
                           'parent_id': 1,
                           'order': 0}],
                         # Current level
                         [{'menu_id': 1,
                           'name': 'I3',
                           'url': '/i3',
                           'class': 'current',
                           'id': 3,
                           'parent_id': 2,
                           'order': 0},
                          {'menu_id': 1,
                           'name': 'I32',
                           'url': '/i32',
                           'class': 'neighbour',
                           'id': 32,
                           'parent_id': 2,
                           'order': 0}],
                         # Child level
                         [{'menu_id': 1,
                           'name': 'I4',
                           'url': '/i4',
                           'class': 'child',
                           'id': 4,
                           'parent_id': 3,
                           'order': 0},
                          {'menu_id': 1,
                           'name': 'I41',
                           'url': '/i41',
                           'class': 'child',
                           'id': 41,
                           'parent_id': 3,
                           'order': 0}]]}
    """
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

        def get_children(node, item_class=None):
            """Build result list for menu, check URLs, add classes."""
            current_level = dict_menu.get(node)

            for item in current_level:
                if '/' not in item['url']:
                    try:
                        item['url'] = reverse(item['url'])
                    except NoReverseMatch:
                        item['url'] = '#'

                if item_class:
                    item['class'] = item_class
                elif item['url'] == current_url_name or \
                        item['url'] == current_path:
                    item['class'] = 'current'
                    # Get children if exist
                    if dict_menu.get(item['id']):
                        get_children(item['id'], item_class='child')
                elif dict_menu.get(item['id']):
                    item['class'] = 'selected'
                    get_children(item['id'])
                elif not item['parent_id']:
                    item['class'] = 'root'
                else:
                    item['class'] = 'neighbour'

            result_menu.append(current_level)

        get_children(None)
        result_menu.reverse()
    else:
        logging.error('menu with name "{}" is empty'.format(menu_name))

    return {'levels': result_menu, 'menu_name': menu_name}

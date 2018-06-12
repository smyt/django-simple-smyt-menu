===========
Django Menu
===========

Simple django app for menu displaying.
Developed for testing task.
Task condition:

1. Develop menu with template tag.

2. Expand menu items above current menu item. First level of nesting has to be expanded too.

3. Store menu items in database.

4. Enable menu editing through standard django admin.

5. Menu item is active when current page URL is equal to menu item's URL.

6. Multiple menus on one page. Identify menu with its name.

7. Go to linked URL when menu item clicked. URL may be defined as string, or with Django's named URL.

8. Additional task: use one query for one menu show.

9. Use Django and standard Python library only.

Quick start
-----------

1. Install package to environment::

   python setup.py install

2. Run tests::

   ./runtests.py

3. Add "menu" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'menu',
    ]

4. Load app tags to template like this::

    {% load menus %}


5. Run `python manage.py migrate` to create the menus models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a menu with items (you'll need the Admin app enabled).

7. Use `draw_sql_menu` or `draw_orm_menu` tag with menu name to show menu on page::

    {% draw_raw_menu 'main' %}
    {% draw_sql_menu 'main' %}

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from menu.models import Item
from menu.models import Menu


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = ()
    list_display = ('menu', 'name')
    list_display_links = ('name',)
    list_select_related = ('menu',)
    search_fields = ('name',)
    ordering = ('menu', 'parent', 'order', 'name')

    def save_model(self, request, obj, form, change):
        super(ItemAdmin, self).save_model(request, obj, form, change)


class ItemInline(admin.TabularInline):
    model = Item
    ordering = ('menu', 'parent', 'order', 'name')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [
        ItemInline,
    ]

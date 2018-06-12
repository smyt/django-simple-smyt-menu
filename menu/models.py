# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.urls import resolve
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls.exceptions import Resolver404
from django.urls.exceptions import NoReverseMatch


class Menu(models.Model):
    ''' Menu '''
    name = models.CharField(max_length=80, help_text='For template')
    depth = models.IntegerField(default=3, help_text='Maximum nesting level, used for orm tag only')

    class Meta:
        verbose_name = 'menu'
        verbose_name_plural = 'menus'

    def __unicode__(self):
        return self.name


class Item(models.Model):
    ''' Menu Item '''
    menu = models.ForeignKey('Menu',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    parent = models.ForeignKey('Item',
                               on_delete=models.CASCADE,
                               related_name='children',
                               null=True,
                               blank=True)
    order = models.PositiveIntegerField(default=0)
    url = models.CharField(max_length=100, default='', blank=True)

    class Meta:
        verbose_name = 'menu item'
        verbose_name_plural = 'menu items'
        unique_together = (('menu', 'url'))

    def __unicode__(self):
        return u'{} - {}'.format(self.menu.name, self.name)

    def clean(self, exclude=None):

        # do not allow set self as parent
        if self.parent_id:
            if self.parent_id == self.id:
                raise ValidationError('Parent is equal to itself')
            if self.menu != self.parent.menu:
                raise ValidationError('Bad parent')

        # check correct URL
        if '/' not in self.url:  # for named URL
            try:
                reverse(self.url)
            except NoReverseMatch:
                raise ValidationError('Bad URL')

        elif self.url.startswith('/'):  # for raw internal URL
            try:
                resolve(self.url)
            except Resolver404:
                raise ValidationError('Bad URL')

        else:  # for raw external URL
            validate = URLValidator()
            validate(self.url)

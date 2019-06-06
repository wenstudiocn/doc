#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import json
import logging

import re

from django import template

register = template.Library()

from datetime import date

from django.template import defaultfilters
from django.utils.timezone import is_aware, utc
from django.utils.translation import pgettext, ugettext as _, ungettext
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

# register = template.Library()


@register.filter(name='avatar')
def avatar(value):
    return value.replace("{size}", "45")


@register.filter(name='from_zulu')
def from_zulu(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        return ""


@register.filter(name='seo_url')
def seo_url(value):
    return value.replace("_", "-")


@register.filter(name='capitalize')
def capitalize(value):
    return value.capitalize()


@register.filter(name='to_json')
def to_json(o):
    return mark_safe(json.dumps(o)) if o else ''


@register.filter(name='prettytime')
def prettytime(value):
    """
    Based on Djangos naturaltime
    """
    if not isinstance(value, date):  # datetime is a subclass of date
        return value

    now = datetime.datetime.now(utc if is_aware(value) else None)
    if value < now:
        delta = now - value
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timesince(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return 'less than a minute ago'
        elif delta.seconds // 60 < 10:
            count = delta.seconds // 60
            return 'a few minutes ago'
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a minute ago', '%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'an hour ago', '%(count)s hours ago', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timeuntil(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a second ago', '%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'a minute ago', '%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: please keep a non-breaking space (U+00A0)
                # between count and time unit.
                'an hour ago', '%(count)s hours ago', count
            ) % {'count': count}


@register.filter(name='to_latin')
def to_latin(value):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

    tr = {ord(a): ord(b) for a, b in zip(*symbols)}

    return value.translate(tr)


@register.filter(name='forum_user_links')
def forum_user_links(value, forum_base='https://forum.defold.com'):
    return re.sub('href=\"\/users\/', 'target="_blank" href="%s/users/' % forum_base, value)


@register.filter(name='is_integer')
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


@register.filter(name='strip_protocol')
def strip_protocol(value):
    if not value:
        return value
    else:
        return re.sub(r'^https?://', '', value)


@register.filter(name='ensure_protocol')
def ensure_protocol(value):
    if not value:
        return value

    if re.search(r'^https?://', value):
        return value
    else:
        return 'http://' + value


@register.filter(name='range')
def _range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)


@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg


@register.filter(name='modulo')
def modulo(value, arg):
    return value % arg


@register.filter(name='youtube_id_from_url')
def youtube_id_from_url(value):
    if not value:
        return value
    else:
        regex = r'^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$'
        match = re.search(regex, value)
        if match:
            return match.group(1)
        else:
            return None


@register.filter(name='youtube_thumbnail_from_id')
def youtube_thumbnail_from_id(value, size='default'):
    if not value:
        return value
    else:
        return 'https://img.youtube.com/vi/%s/%s.jpg' % (value, size)

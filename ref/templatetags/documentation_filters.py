import re

from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import LuaLexer

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    return value[arg]


@register.filter(name='parameter_fragment')
def parameter_type(params):
    ps = []
    for p in params:
        ps.append(p['name'])
    params = ','.join(ps)
    if params == '':
        return ''
    else:
        return ':' + re.sub(r'[^a-zA-Z0-9-_:.]', '-', params)


@register.filter(name='parameter_type')
def parameter_type(value):
    # Parameter types are written (type1 or type2) or (type1|type2)
    exp = r'\((([a-z0-9_]+([|]|[ ]or[ ])*)+)\)'
    match = re.search(exp, value,)
    if match:
        match = match.group(1)
    value = re.sub(exp, '', value)
    if match:
        # Make sure types are shown as (type1 | type2)
        match = re.sub(' or ', ' | ', match)
        match = re.sub(r'(?<=\w)[|](?=\w)', ' | ', match)
        return '<span class="ref-entry-parameter"><span class="type-cell"><span class="type">%s</span></span> <span class="description-cell">%s</span></span>' % (match, value)
    else:
        return '<span class="ref-entry-parameter"><span class="description-cell">%s</span></span>' % (value)


@register.filter(name='lua')
def lua(value):
    return prehighlight(value)


def prehighlight(value, direct=False):
    match = re.search(r'(.*?)<pre>(.*?)<\/pre>(.*)', value, re.DOTALL)
    if match:
        value = "%s%s%s" % (match.group(1), highlight(match.group(2), LuaLexer(), HtmlFormatter()), prehighlight(match.group(3)))
        return value

    return value

from django import template
from django.template.defaultfilters import stringfilter

#for custom filters in templates
register = template.Library()

@register.filter(name='replaceSpace')
@stringfilter
def replaceSpace(value,arg):
    return value.replace(' ',arg)

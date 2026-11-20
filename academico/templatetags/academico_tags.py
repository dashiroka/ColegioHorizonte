from django import template
register=template.Library()
@register.filter
def field(obj,name):
    return getattr(obj,name,'')

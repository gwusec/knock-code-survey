from django import template
import json

register = template.Library()

@register.filter
def split(value, arg):
    if not value: return []
    """Removes all values of arg from the given string"""
    return json.dumps(value.split(arg))


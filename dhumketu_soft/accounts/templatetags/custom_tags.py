# templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def startswith(text, prefix):
    if isinstance(text, str):
        return text.startswith(prefix)
    return False
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

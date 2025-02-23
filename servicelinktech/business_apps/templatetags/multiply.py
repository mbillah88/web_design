
from django import template
import inflect

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def subtraction(value, arg):
    return value - arg


@register.filter
def addition(value, arg):
    return value + arg

@register.filter
def number_to_words(value):
    p = inflect.engine()
    return p.number_to_words(value)
    
@register.filter
def startswith(value, arg):
    return value.startswith(arg)
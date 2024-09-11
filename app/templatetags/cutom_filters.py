from django import template

register = template.Library()

@register.filter
def divide_by_hundred(value):
    return value / 100
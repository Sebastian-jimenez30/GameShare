from django import template

register = template.Library()

@register.filter
def make_groups(value, n):
    n = int(n)
    return [value[i:i + n] for i in range(0, len(value), n)]

from django import template
register = template.Library()

@register.filter
def addcss(field, css):
    attributes = dict()
    pairs = css.split('|')

    for pair in pairs:
        key, value = pair.split(',')
        attributes[key] = value

    return field.as_widget(attrs=attributes)

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(list_data, index):
    try:
        return list_data[index]
    except (IndexError, TypeError):
        return ''

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    try:
        return dictionary.get(key, '')
    except (AttributeError, TypeError):
        return ''

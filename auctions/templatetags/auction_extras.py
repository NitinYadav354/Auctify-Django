from django import template

register = template.Library()

@register.filter(name="get_range") 
def get_range(number):
    return range(number)

@register.filter(name="get_item")
def get_item(dictionary,key):
    return dictionary[key] 
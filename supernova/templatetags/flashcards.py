from django import template

register = template.Library()

@register.filter

def get_rag(fc, user):
    return fc.get_rag(user)
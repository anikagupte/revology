from django import template

register = template.Library()

@register.filter

def preview_note(note, num):
    return note.preview_note(note, num)
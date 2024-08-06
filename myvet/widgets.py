from django import forms
from django.utils.safestring import mark_safe

class ReadOnlyListWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None or value is []:
            return mark_safe(f'<p>No items</p>')
        elif isinstance(value, str):
            value = value.split(', ')
        list_items = ''.join([f'<li style="padding: 0.25rem 0.5rem; border: 1px solid #fff; border-radius: 5px">{item}</li>' for item in value])
        return mark_safe(f'<ul style="margin-left: 0; padding-inline: 0; display: flex; flex-direction: row; gap: 0.5rem">{list_items}</ul>')
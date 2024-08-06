from django import forms
from .models import Pet, Client
from .widgets import ReadOnlyListWidget
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

class PetForm(forms.ModelForm):
    vaccines = forms.CharField(label=mark_safe(f'<strong>Vaccines</strong>'), required=False, widget=ReadOnlyListWidget)

    class Meta:
        model = Pet
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.vaccines:
            self.fields['vaccines'].initial = ', '.join(self.instance.vaccines)

class ClientForm(forms.ModelForm):
    pets = forms.CharField(label=mark_safe(f'<strong>Pets</strong>'), required=False, widget=ReadOnlyListWidget)

    class Meta:
        model = Client
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pets:
            self.fields['pets'].initial = ', '.join(self.instance.pets)
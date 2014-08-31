# -*- encoding: utf-8 -*-

from django import forms
from django.core import validators


user_validator = validators.RegexValidator(
    regex = r'^[a-zA-Z0-9_]{3,15}$',
    message = u'Debe ser una palabra de 3 a 15 letras o números, o guión bajo "_"',
)

class UserProfileEditPersonalForm(forms.Form): # Cannot be a ModelForm because edits data of two models at the same time
    username = forms.CharField(
        max_length=30, required=True,
        validators=[user_validator,]
    )
    email = forms.EmailField( # Note that it is allowed to have several users with same email. This is useful, for example,
        required=True,        # for the case in that a single person manages the inscription of several friends.
    )
    password1 = forms.CharField(
        min_length = 5, max_length=30, required=False,
        widget = forms.PasswordInput,
    )
    password2 = forms.CharField(
        min_length = 5, max_length=30, required=False,
        widget = forms.PasswordInput,
    )
    first_name = forms.CharField(
        max_length=100, required=True,
    )
    last_name = forms.CharField(
        max_length=100, required=True,
    )
    alias = forms.CharField(
        max_length=100, required=False,
    )
    smial = forms.CharField(
        max_length=100, required=False,
    )
    phone = forms.CharField(
        max_length=100, required=True,
    )
    city = forms.CharField(
        max_length=100, required=False,
    )
    age = forms.IntegerField(
        min_value = 1, max_value = 100, required=True,
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.initial['username']:
            from django.contrib.auth.models import User
            if User.objects.filter(username = username).count() > 0:
                raise validators.ValidationError(
                    u'Ese usuario ya existe, por favor introduce otro nombre',
                )
        return username

    def clean(self):
        cleaned_data = super(UserProfileEditPersonalForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                # See https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
                self._errors['password1'] = self.error_class([u'Las dos contraseñas no coinciden'])
                del cleaned_data['password1']
                del cleaned_data['password2']
        return cleaned_data



class UserProfileEditInscriptionForm(forms.Form):
    notes_food = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    notes_transport = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    notes_general = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    dinner_menu = forms.ChoiceField(
        required = True,
        choices = (('carne','carne'), ('pescado','pescado'), ('otros','otros')),
    )
    shirts_S = forms.IntegerField(
        min_value = 0, initial = 0, required=True,
    )
    shirts_M = forms.IntegerField(
        min_value = 0, initial = 0, required=True,
    )
    shirts_L = forms.IntegerField(
        min_value = 0, initial = 0, required=True,
    )
    shirts_XL = forms.IntegerField(
        min_value = 0, initial = 0, required=True,
    )
    shirts_XXL = forms.IntegerField(
        min_value = 0, initial = 0, required=True,
    )


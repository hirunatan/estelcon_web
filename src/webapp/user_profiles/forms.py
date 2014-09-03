# -*- encoding: utf-8 -*-

from django import forms
from django.core import validators

from core import services


user_validator = validators.RegexValidator(
    regex = r'^[a-zA-Z0-9_]{3,15}$',
    message = u'Debe ser una palabra de 3 a 15 letras o números, o guión bajo "_"',
)


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=30, required=True,
        validators=[user_validator,]
    )
    email = forms.EmailField( # Note that it is allowed to have several users with same email. This is useful, for example,
        required=True,        # for the case in that a single person manages the inscription of several friends.
    )
    password1 = forms.CharField(
        min_length = 5, max_length=30, required=True,
        widget = forms.PasswordInput,
    )
    password2 = forms.CharField(
        min_length = 5, max_length=30, required=True,
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
    day_1 = forms.BooleanField(
        initial = True, required = False,
    )
    day_2 = forms.BooleanField(
        initial = True, required = False,
    )
    day_3 = forms.BooleanField(
        initial = True, required = False,
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

    def clean_username(self):
        username = self.cleaned_data['username']
        if services.retrieve_user(username):
            raise validators.ValidationError(
                u'Ese usuario ya existe, por favor introduce otro nombre.',
            )
        return username

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                # See https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
                self._errors['password1'] = self.error_class([u'Las dos contraseñas no coinciden.'])
                if password1:
                    del cleaned_data['password1']
                if password2:
                    del cleaned_data['password2']

        day_1 = cleaned_data.get('day_1')
        day_2 = cleaned_data.get('day_2')
        day_3 = cleaned_data.get('day_3')
        if not day_1 and not day_2 and not day_3:
            err = self.error_class([u'Debes indicar al menos uno de estos.'])
            self._errors['day_1'] = err
            self._errors['day_2'] = err
            self._errors['day_3'] = err
            if day_1 is not None:
                del cleaned_data['day_1']
            if day_2 is not None:
                del cleaned_data['day_2']
            if day_3 is not None:
                del cleaned_data['day_3']

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30, required=True,
    )
    password = forms.CharField(
        max_length=30, required=True,
        widget = forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = services.authenticate_user(username, password)

        if user is None:
            raise validators.ValidationError(u'Este usuario no existe o la contraseña es incorrecta.')
        if not user.is_active:
            raise validators.ValidationError(u'Este usuario está desactivado.')

        cleaned_data['user'] = user

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=30, required=True,
    )

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()

        username = self.cleaned_data['username']

        user = services.retrieve_user(username)
        if not user:
            self._errors['username'] = self.error_class([u'Ese nombre de usuario no existe.'])
            del cleaned_data['username']
        else:
            cleaned_data['user'] = user

        return cleaned_data


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(
        min_length = 5, max_length=30, required=True,
        widget = forms.PasswordInput,
    )
    password2 = forms.CharField(
        min_length = 5, max_length=30, required=True,
        widget = forms.PasswordInput,
    )
    reminder_code = forms.CharField(
        required=True,
        widget = forms.HiddenInput,
    )

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                # See https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
                self._errors['password1'] = self.error_class([u'Las dos contraseñas no coinciden.'])
                if password1:
                    del cleaned_data['password1']
                if password2:
                    del cleaned_data['password2']

        reminder_code = self.cleaned_data['reminder_code']
        user = services.validate_reminder_code(reminder_code)
        if not user:
            self._errors['reminder_code'] = self.error_class([u'El código de recuperación de contraseña no es válido o está caducado. Por favor, vuelve a la página de entrada y empieza de nuevo.'])
            del cleaned_data['reminder_code']
        else:
            cleaned_data['user'] = user

        return cleaned_data


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
            if services.retrieve_user(username):
                raise validators.ValidationError(
                    u'Ese usuario ya existe, por favor introduce otro nombre.',
                )
        return username

    def clean(self):
        cleaned_data = super(UserProfileEditPersonalForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                # See https://docs.djangoproject.com/en/1.6/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
                self._errors['password1'] = self.error_class([u'Las dos contraseñas no coinciden.'])
                if password1:
                    del cleaned_data['password1']
                if password2:
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


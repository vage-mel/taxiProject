from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import *
from django.forms.extras.widgets import SelectDateWidget

from apps.your_taxi.models import City
from .models import Car, User


class FormCreateOrder(forms.Form):
    From = forms.CharField(
        label='Откуда',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input__field input__field--nao', 'placeholder': 'Улица, номер дома'})
    )

    to = forms.CharField(
        label='Куда',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input__field input__field--nao', 'placeholder': 'Улица, номер дома'})
    )

    cost = forms.IntegerField(
        label='Цена',
        widget=forms.NumberInput(attrs={'class': 'input__field input__field--nao'})
    )

    info_order = forms.CharField(
        label='Примечание',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input__field input__field--nao'})
    )


class CommentCreationForm(forms.Form):
    text = forms.CharField(
        label='Отзыв о заказе',
        widget=forms.Textarea(attrs={'class': 'message'})
    )


class CarCreationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('number', 'mark', 'model', 'year_issue', 'color')

    def __init__(self, *args, **kwargs):
        super(CarCreationForm, self).__init__(*args, **kwargs)

        if self.errors:
            for f_name in self.fields:
                if f_name in self.errors:
                    classes = self.fields[f_name].widget.attrs.get('class', '')
                    classes += ' error-field'
                    self.fields[f_name].widget.attrs['class'] = classes


class CarChangeForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('number', 'mark', 'model', 'year_issue', 'color')

    def __init__(self, *args, **kwargs):
        super(CarChangeForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].widget.attrs.update({'class': 'form-field'})


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'password',
            'email',
            'first_name',
            'last_name',
            'city'
        )

        def __init__(self, *args, **kwargs):
            super(UserCreationForm, self).__init__(*args, **kwargs)

            if self.errors:
                for f_name in self.fields:
                    if f_name in self.errors:
                        classes = self.fields[f_name].widget.attrs.get('class', '')
                        classes += ' error-field'
                        self.fields[f_name].widget.attrs['class'] = classes

    city = forms.ModelChoiceField(label='Город', queryset=City.objects.all())

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 5:
            raise forms.ValidationError("Введите пароль не менее 5 символов")

        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        try:
            user = User.objects.get(phone_number=phone_number)
            raise ValidationError('Данный номер занят.')
        except ObjectDoesNotExist:
            return self.cleaned_data['phone_number']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        password = self.cleaned_data["password"]

        if password:
            user.set_password(password)
        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].widget.attrs.update({'class': 'form-field'})

    password = ReadOnlyPasswordHashField(
        widget=forms.PasswordInput,
        required=False,
        label='Пароль',
    )

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        password = self.cleaned_data["password"]
        if password:
            user.set_password(password)
        if commit:
            user.save()

        return user


class DriverCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            'password',
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'city',
            'sex',
            'is_driver'
        )

        widgets = {
            'date_of_birth': SelectDateWidget(years=range(1960, 2008)),
        }

    def __init__(self, *args, **kwargs):
        super(DriverCreationForm, self).__init__(*args, **kwargs)

        if self.errors:
            for f_name in self.fields:
                if f_name in self.errors:
                    classes = self.fields[f_name].widget.attrs.get('class', '')
                    classes += ' error-field'
                    self.fields[f_name].widget.attrs['class'] = classes

    city = forms.ModelChoiceField(label='Город', queryset=City.objects.all())

    def save(self, commit=True):
        user = super(DriverCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

        return user

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 5:
            raise forms.ValidationError("Введите пароль не менее 5 символов")

        return password


class DriverChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].widget.attrs.update({'class': 'form-field'})

    password = ReadOnlyPasswordHashField(
        widget=forms.PasswordInput,
        required=False,
        label='Пароль',
    )

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        password = self.cleaned_data["password"]
        if password:
            user.set_password(password)
        if commit:
            user.save()

        return user
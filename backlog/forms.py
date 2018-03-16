from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import UserManager
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


class TaskModificationForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Name',

    }))
    importance = forms.IntegerField(max_value=10, min_value=1, widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Importance',
        'type': 'number',
        'min': '1',
        'step': '1',
        'max': '10'

    }))
    dead_line = forms.DateField(widget=forms.TextInput(attrs=
    {
        'id': 'datepicker',
        'class': 'form-control',
        'placeholder': 'Importance',

    }))
    description = forms.CharField(max_length=500, widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Description',

    }))
    uList = []
    users = ()
    object = UserManager()
    all_users = User.object.all()
    users += ((None, '-----------------------'),)
    for i in all_users:
        users += ((i, str(i.id) + '. ' + i.first_name + ' ' + i.last_name),)
    assigned_user = forms.ChoiceField(required=False, choices=users, widget=forms.Select(attrs=
    {
        'class': 'form-control selectpicker '

    }))


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'active', 'admin')

    def clean_password(self):
        """Regardless of what the user provides, return the initial value.
            This is done here, rather than on the field, because the
            field does not have access to the initial value
            """
        return self.initial["password"]


class NewSprint(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    dead_line = forms.DateField(widget=forms.TextInput(attrs=
    {
        'id': 'datepicker',
        'class': 'form-control',
        'placeholder': 'Date'
    }))


class NewBackLog(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    dead_line = forms.DateField(widget=forms.TextInput(attrs=
    {
        'id': 'datepicker',
        'class': 'form-control',
        'placeholder': 'Date'
    }))


class NewTask(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Name'
    }))
    dead_line = forms.DateField(widget=forms.TextInput(attrs=
    {
        'id': 'datepicker',
        'class': 'form-control',
        'placeholder': 'Date'
    }))
    description = forms.CharField(max_length=500, widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'description'
    }))
    importance = forms.IntegerField(max_value=10, min_value=1, widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Importance',
        'type': 'number',
        'min': '1',
        'step': '1',
        'max': '10'

    }))


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Email',
        'type': 'email'
    }))
    password = forms.CharField(widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Password',
        'type': 'password'
    }))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")

        object = UserManager()
        qs = User.object.filter(email=email)

        if qs.exists():
            # user email is registered, check active
            not_active = qs.filter(active=False)
            print(not_active.exists())
            if not_active.exists():
                raise forms.ValidationError("This user is inactive.")

        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request, user)
        self.user = user
        return data


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='', widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Password',
        'type': 'password'
    }))
    password2 = forms.CharField(label='', widget=forms.TextInput(attrs=
    {
        'class': 'form-control',
        'placeholder': 'Password',
        'type': 'password'
    }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.active = False
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email',
            'type': 'email'
        })
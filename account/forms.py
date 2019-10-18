from django import forms


class SignUpForm(forms.Form):
    """
    The login form.
    """
    username = forms.CharField(max_length=30, required=True)
    gender = forms.ChoiceField(choices=((0, '--Select--'), (1, 'Male'), (2, 'Female')),)
    contact_number = forms.CharField(required=True)
    password = forms.CharField(widget=forms.widgets.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput(), required=True)

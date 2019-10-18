from django import forms


class HomeForm(forms.Form):
    """
    The login form.
    """
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.widgets.PasswordInput(), required=True)

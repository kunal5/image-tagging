from django import forms


class SecondaryImageForm(forms.Form):
    """
    The login form.
    """
    images = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,

    )

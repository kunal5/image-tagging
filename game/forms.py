# from django import forms
# from django.utils.safestring import mark_safe
# from game.models import SecondaryImages
#
#
# class CustomChoiceField(forms.ModelMultipleChoiceField):
#
#     def label_from_instance(self, obj):
#         return mark_safe("<img src='%s' style='width:260px; height:160px' class='cls_secondaryimage_%s'/>" %
#                          (obj.secondary_image, obj.pk))
#
#
# class SecondaryImageForm(forms.Form):
#
#     # def __init__(self, *args, **kwargs):
#     #     # first call parent's constructor
#     #     super(SecondaryImageForm, self).__init__(*args, **kwargs)
#     #     # there's a `fields` property now
#     #     import ipdb; ipdb.set_trace()
#     #     self.fields['secondary_image'].required = False
#
#     Options = CustomChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'checked': False}),
#                                 queryset=SecondaryImages.objects.all())
#
#     # class Meta:
#     #     model = SecondaryImages
#     #     fields = ['secondary_image']
#
#
# # class SecondaryImageForm(forms.Form):
# #     """
# #     The login form.
# #     """
# #     images = forms.MultipleChoiceField(
# #         widget=forms.CheckboxSelectMultiple,
# #
# #     )

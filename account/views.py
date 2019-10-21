from django.shortcuts import render
from django.views.generic import FormView
from django.http import HttpResponseRedirect
from account.forms import SignUpForm
from account.models import Participants
# Create your views here.


class SignUpView(FormView):
    """Sign Up View"""
    form_class = SignUpForm
    template_name = 'signup.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        if Participants.objects.filter(username=username).exists():
            return render(self.request, self.template_name, {
                'error_msg': 'Username already exists!',
                'form': form
            })
        gender = form.cleaned_data['gender']
        contact_number = form.cleaned_data['contact_number']
        password = form.cleaned_data['password']
        new_password = form.cleaned_data['confirm_password']
        if gender == '0':
            return render(self.request, self.template_name, {
                'error_msg': 'Please select a gender',
                'form': form
            })
        if password != new_password:
            return render(self.request, self.template_name, {
                'error_msg': 'Password does not match!',
                'form': form
            })
        user = Participants(username=username, gender=gender, contact_number=contact_number)
        user.set_password(password)
        user.save()
        return HttpResponseRedirect('/home/login/?success=1')

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'error_msg': 'There are some errors in form',
            'form': form
        })


def redirect_view(request):
    return HttpResponseRedirect('/home/login/')

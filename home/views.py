from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponseRedirect
from django.db.models import Q
from account.models import Participants
from game.models import PrimaryImages, SecondaryImages, Game, SharedPair
from home.forms import HomeForm
# Create your views here.


class HomeView(FormView):
    """Home View"""
    form_class = HomeForm
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/game/')
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        success = request.GET.get('success', None)
        valid = request.GET.get('valid', None)
        logout = request.GET.get('logout', None)
        if success:
            return render(request, self.template_name, {
                'success': 'Your credentials have been saved successfully. Please login to continue',
                'form': HomeForm()
            })
        elif valid == '0':
            return render(request, self.template_name, {
                'error_msg': 'Please login to continue',
                'form': HomeForm()
            })
        elif logout:
            return render(request, self.template_name, {
                'success': 'You have been logged out successfully!',
                'form': HomeForm()
            })
        else:
            return render(request, self.template_name, {
                'form': HomeForm()
            })

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # Authenticate User
        user = authenticate(request=self.request, username=username, password=password)
        if user is None:
            return render(self.request, self.template_name, {
                'error_msg': 'Username and Password does not match!',
                'form': form
            })
        else:
            login(self.request, user)
            primary_images = list(PrimaryImages.objects.all().values_list('primary_image', flat=True))
            self.request.session['primary_images'] = ','.join(list(PrimaryImages.objects.all().values_list(
                'primary_image', flat=True)))
            self.request.session['secondary_images'] = ','.join(list(SecondaryImages.objects.all().values_list(
                'secondary_image', flat=True)))
            Participants.objects.filter(username=username).update(is_loggedin=True)
            return HttpResponseRedirect('/game/')

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'error_msg': 'There are some errors in form',
            'form': form
        })


class HomeLogOutView(TemplateView):
    """Home Logout View"""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            Participants.objects.filter(username=request.user.username).update(is_loggedin=False,
                                                                               searching_pair=False,
                                                                               started_playing=False)
            Game.objects.filter(Q(player1=request.user) | Q(player2=request.user)).update(is_playing=False)
            SharedPair.objects.filter(Q(sharedplayer1=request.user) | Q(sharedplayer2=request.user)).update(
                is_pair=False)
            logout(request)
            return HttpResponseRedirect('/home/login/?logout=1')

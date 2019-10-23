import random
import json
import time

from django.shortcuts import render
from django.db.models import Q
from django.views.generic import CreateView, FormView
from django.http import JsonResponse, HttpResponseRedirect
from account.models import Participants
from game.models import PrimaryImages, SecondaryImages, Game, SharedPair

# Create your views here.


class GameView(CreateView):
    template_name = 'game.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/home/login/?valid=0')
        return super(GameView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        current_player = request.GET.get('started_playing', None)
        if current_player:
            sharedpair = SharedPair.objects.filter(Q(sharedplayer1=request.user) | Q(sharedplayer2=request.user),
                                                   is_pair=True)

            loggedin_player = Participants.objects.get(username=current_player)

            if current_player != sharedpair[0].sharedplayer1.username:
                partner = sharedpair[0].sharedplayer1
            else:
                partner = sharedpair[0].sharedplayer2

            if not loggedin_player.started_playing:
                partner.started_playing = True
                partner.save()
            # Participants.objects.filter(username=current_player).update(started_playing=True)
            if not loggedin_player.started_playing:
                while True:
                    if not sharedpair[0].question and not sharedpair[0].options and not sharedpair[0].game:
                        sharedpair = SharedPair.objects.filter(
                            Q(sharedplayer1=request.user) | Q(sharedplayer2=request.user),
                            is_pair=True)
                        continue
                    else:
                        break
            return JsonResponse({'valid': True}, safe=False)
        else:
            Participants.objects.filter(username=request.user.username).update(searching_pair=False,
                                                                               started_playing=False)
            Game.objects.filter(Q(player1=request.user) | Q(player2=request.user)).update(is_playing=False)
            SharedPair.objects.filter(Q(sharedplayer1=request.user) | Q(sharedplayer2=request.user)).update(
                is_pair=False)
            return render(request, self.template_name, {
                'show_game_button': True,
                'user': request.user
            })

    def post(self, request, *args, **kwargs):
        player1 = None
        player2 = None
        available_players = Participants.objects.filter(is_loggedin=True, searching_pair=True).exclude(
            username=request.user.username)
        if available_players.count() >= 1:
            player1 = Participants.objects.get(username=request.user.username)
            player2 = self.generate_random_pair(available_players)
            Participants.objects.filter(username=request.user.username).update(searching_pair=False)
            SharedPair.objects.create(sharedplayer1=player1, sharedplayer2=player2, is_pair=True)
        else:
            Participants.objects.filter(username=request.user.username).update(searching_pair=True)
            while True:
                # available_players = Participants.objects.filter(is_loggedin=True, searching_pair=True).exclude(
                #     username=request.user.username)
                if SharedPair.objects.filter(sharedplayer2=request.user, is_pair=True):
                    player2 = SharedPair.objects.filter(sharedplayer2=request.user, is_pair=True)[0].sharedplayer1
                    player1 = request.user
                    Participants.objects.filter(username=player1.username).update(searching_pair=False)
                    break
                # if available_players.count() >= 1:
                #     # Participants.objects.filter(username=request.user.username).update(searching_pair=False)
                #     break
                # elif Participants.objects.filter(username=request.user.username, searching_pair=False):
                #     break
                else:
                    time.sleep(2)
                    continue
        # if not player2:
        #     player2 = self.generate_random_pair(available_players)
        # Participants.objects.filter(username=request.user.username).update(searching_pair=False)
        data = {
            'player1': player1.username,
            'player2': player2.username,
        }
        return JsonResponse(data, safe=False)

    def generate_random_pair(self, available_players):
        available_players_count = available_players.count()
        # Generating player 2 random distinct index for the first time
        pIndex = self.generate_random_indexes(available_players_count)
        player2_already_playing, player2 = self.check_if_player_playing(pIndex, available_players)

        while player2_already_playing:
            # Generating player 2 random distinct index
            pIndex = self.generate_random_indexes(available_players_count)
            player2_already_playing, player2 = self.check_if_player_playing(pIndex, available_players)
        return player2

    def generate_random_indexes(self, available_players_count, *args):
        try:
            pIndex = random.randint(0, available_players_count-1)
        except ValueError:
            pIndex = 0
        return pIndex

    def check_if_player_playing(self, pIndex, available_players):
        player2 = available_players[pIndex]
        player2_already_playing = Game.objects.filter(is_playing=True, player1=player2)
        if not player2_already_playing:
            player2_already_playing = Game.objects.filter(is_playing=True, player2=player2)
        return player2_already_playing, player2


class RoundView(FormView):
    template_name = 'game_rounds.html'

    def get(self, request, *args, **kwargs):
        p1 = request.GET.get('player1')
        p2 = request.GET.get('player2')
        player1 = Participants.objects.get(username=p1)
        player2 = Participants.objects.get(username=p2)
        game = self.get_game(player1, player2)
        sharedpair = self.get_sharedpair(player1, player2)
        primary_indexes, secondary_indexes = self.que_and_ans_in_shared_pair(sharedpair[0], game)

        # print(primary_indexes)
        # print(secondary_indexes)

        return render(request, self.template_name, {
            'primary_indexes': primary_indexes,
            'secondary_indexes': secondary_indexes,
            'primary_images': request.session.get('primary_images', None),
            'secondary_images': request.session.get('secondary_images', None),
            'gameid': game.pk,
            'player1': p1,
            'player2': p2,
            'user': request.user.username,
        })

    def post(self, request, *args, **kwargs):
        answers = request.POST.get('answers', None)
        user = request.POST.get('user', request.user.username)
        user = Participants.objects.get(username=user)
        gameid = request.POST.get('gameid', None)
        game = Game.objects.get(pk=gameid)
        sharedpair = SharedPair.objects.filter(Q(sharedplayer1=user) | Q(sharedplayer2=user),
                                               game=game, is_pair=True).prefetch_related(
            'sharedplayer1', 'sharedplayer2', 'game')[0]
        if sharedpair.sharedplayer1 == user:
            sharedpair.sharedplayer1_que_and_ans = answers
        elif sharedpair.sharedplayer2 == user:
            sharedpair.sharedplayer2_que_and_ans = answers
        sharedpair.save()
        if game.is_playing:
            game.is_playing = False
            game.save()

            while True:
                if SharedPair.objects.filter(Q(sharedplayer1=user) | Q(sharedplayer2=user), game=game, is_pair=False):
                    break
            score = Game.objects.get(pk=gameid).score


        else:
            score = self.getFinalScore(sharedpair, user, game)
            # Storing the score in database
            game.score = score
            game.is_playing = False
            game.save()
            sharedpair.is_pair = False
            sharedpair.save()
            # print("Inside if %s", sharedpair.__dict__)
        return JsonResponse({'score': score}, safe=False)

    def setFivePrimaryIndexes(self):
        indexes = []
        while len(indexes) < 5:
            try:
                random_number = str(random.randint(0, 14))
                if random_number not in indexes:
                    indexes.append(random_number)
            except ValueError:
                pass
        return indexes

    def setSecondaryIndexes(self):
        secondary_indexes = []
        for i in range(5):
            indexes = []
            while len(indexes) < 3:
                try:
                    random_number = str(random.randint(0, 29))
                    if random_number not in indexes:
                        indexes.append(random_number)
                except ValueError:
                    pass
            secondary_indexes.append(','.join(indexes))
        return secondary_indexes

    def que_and_ans_in_shared_pair(self, sharedpair, game):
        # Check if questions and options are set in SharedPair model
        if not sharedpair.question and not sharedpair.options:
            # Set primary images and secondary images for 5 rounds of the game
            primary_indexes = ','.join(self.setFivePrimaryIndexes())
            secondary_indexes = '|'.join(self.setSecondaryIndexes())
            sharedpair.game = game
            sharedpair.question = primary_indexes
            sharedpair.options = secondary_indexes
            sharedpair.save()
        else:
            primary_indexes = sharedpair.question
            secondary_indexes = sharedpair.options
        return primary_indexes, secondary_indexes

    def get_game(self, player1, player2):
        try:
            game = Game.objects.get(player1=player1, player2=player2, is_playing=True)
        except Exception:
            game = None
        if not game:
            try:
                game = Game.objects.get(player1=player2, player2=player1, is_playing=True)
            except Exception:
                game = None
        if not game:
            game = Game.objects.create(player1=player1, player2=player2, score=0, is_playing=True)
        return game

    def get_sharedpair(self, player1, player2):
        sharedpair = SharedPair.objects.filter(sharedplayer1=player1, sharedplayer2=player2,
                                               is_pair=True)
        if not sharedpair:
            sharedpair = SharedPair.objects.filter(sharedplayer1=player2, sharedplayer2=player1,
                                                   is_pair=True)
        return sharedpair

    def getFinalScore(self, sharedpair, user, game):
        while True:
            print('inside')
            answer1 = sharedpair.sharedplayer1_que_and_ans
            answer2 = sharedpair.sharedplayer2_que_and_ans
            if answer1 and answer2:
                break
            else:
                sharedpair = SharedPair.objects.filter(
                    Q(sharedplayer1=user) | Q(sharedplayer2=user), game=game, is_pair=True)[0]
        loggedinuseranswer = None
        nonloggedinuseranswer = None
        partner = None
        final_score = 0
        if user.username in answer1:
            loggedinuseranswer = answer1
            nonloggedinuseranswer = answer2
            if user.username != sharedpair.game.player1.username:
                partner = sharedpair.game.player1
            else:
                partner = sharedpair.game.player2
        else:
            loggedinuseranswer = answer2
            nonloggedinuseranswer = answer1
            if user.username != sharedpair.game.player1.username:
                partner = sharedpair.game.player1
            else:
                partner = sharedpair.game.player2
            # partner = sharedpair.game.player1

        loggedinuseranswer = json.loads(loggedinuseranswer)
        nonloggedinuseranswer = json.loads(nonloggedinuseranswer)
        # print(sharedpair.game_id, user.username)
        # print('---------------------------------------------------')
        # print(nonloggedinuseranswer)

        # Calculate scores for rounds 1 to 5
        if loggedinuseranswer[str(sharedpair.game_id)][user.username]['round1']['secondaryCheckedImages'] == \
                nonloggedinuseranswer[str(sharedpair.game_id)][partner.username]['round1']['secondaryCheckedImages']:
            final_score += 1
        if loggedinuseranswer[str(sharedpair.game_id)][user.username]['round2']['secondaryCheckedImages'] == \
                nonloggedinuseranswer[str(sharedpair.game_id)][partner.username]['round2']['secondaryCheckedImages']:
            final_score += 1
        if loggedinuseranswer[str(sharedpair.game_id)][user.username]['round3']['secondaryCheckedImages'] == \
                nonloggedinuseranswer[str(sharedpair.game_id)][partner.username]['round3']['secondaryCheckedImages']:
            final_score += 1
        if loggedinuseranswer[str(sharedpair.game_id)][user.username]['round4']['secondaryCheckedImages'] == \
                nonloggedinuseranswer[str(sharedpair.game_id)][partner.username]['round4']['secondaryCheckedImages']:
            final_score += 1
        if loggedinuseranswer[str(sharedpair.game_id)][user.username]['round5']['secondaryCheckedImages'] == \
                nonloggedinuseranswer[str(sharedpair.game_id)][partner.username]['round5']['secondaryCheckedImages']:
            final_score += 1
        return final_score

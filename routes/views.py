from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Route, Point,  Gameboard, Game
from .forms import RouteForm, PointForm, GameboardForm, GameForm
import json


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('route_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def route_list(request):
    routes = Route.objects.filter(user=request.user)
    return render(request, 'routes/list.html', {'routes': routes})


@login_required
def create_route(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()
            return redirect('route_detail', route_id=route.id)
    else:
        form = RouteForm()
    return render(request, 'routes/create.html', {'form': form})


@login_required
def route_detail(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            last_order = route.points \
                .aggregate(Max('order'))['order__max'] or 0
            Point.objects.create(
                route=route,
                x=form.cleaned_data['x'],
                y=form.cleaned_data['y'],
                order=last_order + 1
            )
            return redirect('route_detail', route_id=route.id)
    else:
        form = PointForm()
    points = route.points.all()
    return render(request, 'routes/detail.html',
                  {'route': route, 'form': form, 'points': points})


@login_required
def delete_point(request, route_id, point_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    point = get_object_or_404(Point, id=point_id, route=route)
    if request.method == 'POST':
        point.delete()
    return redirect('route_detail', route_id=route.id)


@login_required
def gameboard_list(request):
    gameboards = Gameboard.objects.filter(user=request.user)
    return render(request, 'gameboard/list.html', {'gameboards': gameboards})


@login_required
def create_gameboard(request):
    if request.method == 'POST':
        form = GameboardForm(request.POST)
        if form.is_valid():
            gameboard = form.save(commit=False)
            gameboard.user = request.user
            gameboard.save()
            return redirect('gameboard_detail', gameboard_id=gameboard.id)
    else:
        form = GameboardForm()
    return render(request, 'gameboard/create.html', {'form': form})


@login_required
def delete_gameboard(request, gameboard_id):
    gameboard = get_object_or_404(Gameboard,
                                  id=gameboard_id, user=request.user)
    gameboard.delete()
    return redirect('gameboard_list')


@login_required
def gameboard_detail(request, gameboard_id):
    gameboard = get_object_or_404(Gameboard,
                                  id=gameboard_id, user=request.user)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')

        print(type(data[0]))

        gameboard.dots = data
        gameboard.save()
        return JsonResponse({'status': 'ok'})

    return render(request, 'gameboard/detail.html',
                  {'gameboard': gameboard, 'dots': gameboard.dots})


@login_required
def game_list(request):
    games = Game.objects.filter(user=request.user)
    return render(request, 'game/list.html', {'games': games})


@login_required
def create_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.user = request.user
            game.save()
            return redirect('play_game', game_id=game.id)
    else:
        form = GameForm()
    return render(request, 'game/create.html', {'form': form})


@login_required
def delete_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    game.delete()
    return redirect('game_list')


@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    return render(request, 'game/play.html', {'gameboard': game.gameboard})

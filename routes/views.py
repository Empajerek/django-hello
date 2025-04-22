from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from .models import Route, Point, BackgroundImage
from .forms import RouteForm, PointForm

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
            last_order = route.points.aggregate(Max('order'))['order__max'] or 0
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
    return render(request, 'routes/detail.html', {'route': route, 'form': form, 'points': points})

@login_required
def delete_point(request, route_id, point_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    point = get_object_or_404(Point, id=point_id, route=route)
    if request.method == 'POST':
        point.delete()
    return redirect('route_detail', route_id=route.id)

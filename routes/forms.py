from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Route, Gameboard

class PointForm(forms.Form):
    x = forms.IntegerField()
    y = forms.IntegerField()

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['background', 'name']

class GameboardForm(forms.ModelForm):
    class Meta:
        model = Gameboard
        fields = ['name', 'rows', 'cols']

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'), #general entry point
    path("optout", views.optout,name="optout"), #for opting out
    path('mturk', views.mturk,name='mturk'), # for loading in mturk
    path('mturk/externalSubmit', views.mturk_test,name="mturk_test"), #for testing
    path('root', views.root,name='root'), # for loading in mturk
]

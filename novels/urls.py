# novels/urls.py
from django.urls import path
from . import views # Import views from the current directory

app_name = 'novels' # Namespace for URLs within this app

urlpatterns = [
    # Map the root URL of this app ('') to the novel_list view
    path('', views.novel_list, name='novel_list'),
    path('novel/<slug:slug>/', views.novel_detail, name='novel_detail'),

    # We will add paths for novel details and chapter details here later
    # path('novel/<slug:slug>/', views.novel_detail, name='novel_detail'),
    # path('novel/<slug:novel_slug>/chapter/<int:chapter_number>/', views.chapter_detail, name='chapter_detail'),
    path('novel/<slug:novel_slug>/chapter/<int:chapter_number>/', views.chapter_detail, name='chapter_detail'),

]


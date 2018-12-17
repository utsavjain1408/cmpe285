from django.urls import include, path
from django.conf.urls import url
from . import views

urlpatterns = [
    # path('index/', views.index, name='index'),
    # path('login_error/', views.login_error, name='login_error'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('careers/', views.careers, name='careers'),
    path('contact/', views.contact, name='contact'),
    path('select_stock/', views.select_stock, name='select_stock'),
    path('confirm_stock/', views.confirm_stock, name='confirm_stock'),
    path('commit_stock/', views.commit_stock, name='commit_stock'),
    url(r'^', views.home)
]
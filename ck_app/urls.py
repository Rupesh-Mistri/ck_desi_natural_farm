from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('income_tree_recursive/',income_tree_recursive,name='income_tree_recursive'),
    # path('',index,name='index'),
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('cascade_ajax/', cascade_ajax, name='cascade_ajax'),
    path('get_sponser_name_ajax/', get_sponser_name_ajax, name='get_sponser_name_ajax'),
]

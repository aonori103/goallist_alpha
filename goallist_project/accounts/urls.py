from django.urls import path
from .views import (HomeView, RegisterUserView, UserLoginView, UserLogoutView, UserEditView, GoalListView, GoalDetailView, GoalRegistView, GoalEditView, GoalDeleteView, PictGenerate)


app_name = 'accounts'
urlpatterns=[
    path('home/', HomeView.as_view(), name='home'),
    path('user_regist/', RegisterUserView.as_view(), name='user_regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user_edit/<int:pk>', UserEditView.as_view(), name='user_edit'),
    path('goal_list/', GoalListView.as_view(), name='goal_list'),
    path('goal_detail/<int:pk>', GoalDetailView.as_view(), name='goal_detail'),
    path('goal_delete/<int:pk>', GoalDeleteView.as_view(), name='goal_delete'),
    path('goal_regist/', GoalRegistView.as_view(), name='goal_regist'),
    path('goal_edit/<int:pk>', GoalEditView.as_view(), name='goal_edit'),
    path('pict_generate/<int:pk>', PictGenerate.as_view(), name='pict_generate'),
    
]
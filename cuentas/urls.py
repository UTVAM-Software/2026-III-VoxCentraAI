from django.urls import path

from . import views


app_name = 'cuentas'

urlpatterns = [
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.LogoutPageView.as_view(), name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('usuarios/', views.UserListView.as_view(), name='user_list'),
    path('usuarios/nuevo/', views.UserCreateView.as_view(), name='user_create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
    path('usuarios/<int:pk>/eliminar/', views.UserDeleteView.as_view(), name='user_delete'),
    path('usuarios/<int:pk>/contrasena/', views.UserPasswordChangeView.as_view(), name='user_password'),
    path('grupos/', views.GroupListView.as_view(), name='group_list'),
    path('grupos/nuevo/', views.GroupCreateView.as_view(), name='group_create'),
    path('grupos/<int:pk>/editar/', views.GroupUpdateView.as_view(), name='group_update'),
    path('grupos/<int:pk>/eliminar/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('permisos/', views.PermissionListView.as_view(), name='permission_list'),
    path('permisos/nuevo/', views.PermissionCreateView.as_view(), name='permission_create'),
    path('permisos/<int:pk>/editar/', views.PermissionUpdateView.as_view(), name='permission_update'),
    path('permisos/<int:pk>/eliminar/', views.PermissionDeleteView.as_view(), name='permission_delete'),
]

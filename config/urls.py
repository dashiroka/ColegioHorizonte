from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cambiar-clave/', auth_views.PasswordChangeView.as_view(template_name='form.html', success_url='/'), name='password_change'),
    path('', include('academico.urls')),
]

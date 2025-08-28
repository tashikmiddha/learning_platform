from django.contrib import admin
from django.urls import path, include
from courses import views as course_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth routes
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', course_views.register, name='register'),

    # Dashboard/home route
    path('', include('courses.urls')),
]

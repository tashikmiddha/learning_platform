from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),  # Handles "/"
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/chat/', views.lesson_chatbot, name='lesson_chatbot'),
    path('chatbot/', views.global_chatbot, name='chatbot'),
    path('chatbot/<int:course_id>/', views.lesson_chatbot, name='lesson_chatbot'),
    path('curriculum/', views.curriculum, name='curriculum'),
    path('video_summarize/', views.video_summarize, name='video_summarize'),
    path('quiz/', views.quiz, name='quiz'),
]

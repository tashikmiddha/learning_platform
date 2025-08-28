# courses/models.py
from django.db import models
from django.contrib.auth.models import User

# models.py
from django.contrib.auth.models import User
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10)  # 'human', 'ai', 'system'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class StudentProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lessons_completed = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

class Curriculum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    curriculum_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class VideoSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

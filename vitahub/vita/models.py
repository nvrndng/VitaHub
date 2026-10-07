from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    about = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username
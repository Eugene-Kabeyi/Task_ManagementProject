from django.db import models
from django.contrib.auth.models import AbstractUser
     
# Create your models here.

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.username 
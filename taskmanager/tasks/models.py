from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    """Category model for task categorization (stretch goal)"""
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    
    class Meta:
        unique_together = ['name', 'user']
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
     
class Task(models.Model):

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10,  choices=PRIORITY_CHOICES, default='medium')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey( 'Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        """Model-level validation"""

        # Ensure due_date is not in the past
        if self.due_date and self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")

        # Handle completed_at automatically
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

        elif self.status == 'pending' and self.completed_at:
            self.completed_at = None

    def save(self, *args, **kwargs):
        # Run clean() before saving
        self.clean()
        super().save(*args, **kwargs)

    @property #Property decorator to check if task is overdue
    def is_overdue(self):
        if self.due_date and self.status == 'pending':
            return timezone.now().date() > self.due_date
        return False
    
    @property  #Property decorator to calculate days until due date
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None

    def __str__(self):
        return self.title



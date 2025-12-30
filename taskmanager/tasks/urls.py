from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, CategoryViewSet

# Create a router instance
router = DefaultRouter()

# Register ViewSets
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Task, Category
from .serializers import TaskSerializer, TaskUpdateSerializer, CategorySerializer
from .permissions import IsTaskOwner, IsCategoryOwner
# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet responsible for:
    - Listing categories
    - Creating categories
    - Updating categories
    - Deleting categories

    All operations are restricted to the logged-in user's own categories.
    """

    # Serializer that controls how Category data is represented
    serializer_class = CategorySerializer

    # User must be authenticated AND must own the category
    permission_classes = [IsAuthenticated, IsCategoryOwner]

    def get_queryset(self):
        """
        Override default queryset.

        This ensures:
        - Users can ONLY see their own categories
        - Prevents data leakage between users
        """
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign the category to the logged-in user
        when a new category is created.
        """
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet responsible for managing tasks.

    Provides:
    - CRUD operations (create, read, update, delete)
    - Search
    - Ordering
    - Custom task actions (overdue, completed, pending, incomplete)
    """

    # Serializer that defines how Task objects are converted to JSON
    serializer_class = TaskSerializer

    # Only authenticated users who own the task can access it
    permission_classes = [IsAuthenticated, IsTaskOwner]

    # Enable search and ordering functionality
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Fields that can be searched via ?search=
    search_fields = ['title', 'description']

    # Fields allowed for ordering via ?ordering=
    ordering_fields = ['due_date', 'priority', 'created_at', 'updated_at']

    # Default ordering (newest tasks first)
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return ONLY tasks belonging to the logged-in user.

        This is the most important security layer:
        - Users cannot view or modify other users' tasks
        """
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically assign the new task to the logged-in user
        during creation.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override the default create method to:
        - Validate incoming data
        - Save the task
        - Return a custom success message along with task data
        """

        # Convert incoming request data into a serializer
        serializer = self.get_serializer(data=request.data)

        # Validate data (raises 400 error if invalid)
        serializer.is_valid(raise_exception=True)

        # Save task and assign user
        self.perform_create(serializer)

        # Standard DRF headers (e.g. Location)
        headers = self.get_success_headers(serializer.data)

        # Custom success response
        return Response(
            {
                "message": "Task created successfully",
                "task": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Custom endpoint:
        GET /api/tasks/overdue/

        Returns all pending tasks whose due date has passed.
        """

        # Get today's date
        today = timezone.now().date()

        # Filter overdue AND pending tasks
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=today,
            status='pending'
        )

        # Apply pagination if enabled
        page = self.paginate_queryset(overdue_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Return full list if pagination is disabled
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Custom endpoint:
        GET /api/tasks/completed/

        Returns all completed tasks.
        """

        completed_tasks = self.get_queryset().filter(status='completed')

        page = self.paginate_queryset(completed_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Custom endpoint:
        GET /api/tasks/pending/

        Returns all pending tasks.
        """

        pending_tasks = self.get_queryset().filter(status='pending')

        page = self.paginate_queryset(pending_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pending_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def incomplete(self, request, pk=None):
        """
        Custom endpoint:
        PATCH /api/tasks/{id}/incomplete/

        Marks a completed task as pending.
        """

        # Ensure the task exists AND belongs to the logged-in user
        task = get_object_or_404(self.get_queryset(), pk=pk)

        # Prevent unnecessary updates
        if task.status == 'pending':
            return Response(
                {"message": "Task is already pending."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark task as pending and clear completion timestamp
        task.status = 'pending'
        task.completed_at = None
        task.save()

        # Serialize updated task
        serializer = self.get_serializer(task)

        return Response(
            {
                "message": "Task marked as incomplete.",
                "task": serializer.data
            }
        )
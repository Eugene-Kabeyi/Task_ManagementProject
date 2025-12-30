from rest_framework import serializers
from .models import Task, Category
from django.utils import timezone
from django.core.exceptions import ValidationError


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'color']
        read_only_fields = ['id', 'user']
    
    def create(self, validated_data):
        """Create a Category instance with the user from the request context."""
        validated_data['user'] = self.context['request'].user # Set the user from the request context
        return super().create(validated_data) # Call the parent create method

class TaskSerializer(serializers.ModelSerializer):

    # Read-only nested category
    category = CategorySerializer(read_only=True)

    # Write-only category id (SECURE)
    category_id = serializers.PrimaryKeyRelatedField(source='category',
        queryset=Category.objects.none(),  # will be set dynamically
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'due_date',
            'created_at', 'updated_at', 'completed_at',
            'category', 'category_id'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'completed_at', 'user', 'category'
        ]

    def __init__(self, *args, **kwargs):
        """Limit categories to the logged-in user"""
        super().__init__(*args, **kwargs)

        request = self.context.get('request') # Get the request from context
        if request and request.user.is_authenticated: # Check if user is authenticated
            self.fields['category_id'].queryset = Category.objects.filter(
                user=request.user
            )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_due_date(self, value):
        """Ensure due date is in the future (DateField-safe)"""
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def validate_priority(self, value):
        if value not in dict(Task.PRIORITY_CHOICES):
            raise serializers.ValidationError("Invalid priority choice.")
        return value

    def validate_status(self, value):
        """Prevent re-completing an already completed task"""
        if self.instance:
            if self.instance.status == 'completed' and value == 'completed':
                raise serializers.ValidationError(
                    "Task is already completed."
                )
        return value

class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Task status only"""

    class Meta:
        model = Task
        fields = ['status']
        read_only_fields = ['id', 'title', 'description', 'priority',
            'due_date', 'created_at', 'updated_at', 'completed_at', 'user',
            'category']
    
    def validate_status(self, value):
        """Prevent re-completing an already completed task"""
        if self.instance:
            if self.instance.status == 'completed' and value == 'completed':
                raise serializers.ValidationError(
                    "Task is already completed."
                )
        return value
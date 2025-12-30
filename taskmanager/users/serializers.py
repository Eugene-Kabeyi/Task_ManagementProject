from rest_framework import serializers
from .models import CustomUser as User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture']

class RegisterUserSerializer(serializers.ModelSerializer):
    # Password field with validation
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    # Confirm password field
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'password', 'password2']

    def validate(self, attrs): #attrs is a dictionary of the input data
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') # Remove password2 as it's not needed for user creation
        user = User.objects.create(**validated_data) # Create user instance
        user.set_password(validated_data['password']) # Hash the password
        user.save() # Save the user instance
        return user

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
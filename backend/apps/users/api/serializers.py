"""
Сериализаторы для API пользователей и аутентификации.
"""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User, ExtendedGroup

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Расширенный сериализатор для получения JWT токенов.
    
    Добавляет информацию о пользователе в ответ.
    """
    
    def validate(self, attrs):
        """Проверка учетных данных и генерация токенов."""
        # Стандартная валидация
        data = super().validate(attrs)
        
        # Сохраняем IP-адрес последнего входа
        if hasattr(self, 'context') and 'request' in self.context:
            request = self.context['request']
            user = self.user
            
            # Получаем IP-адрес
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Сохраняем IP-адрес
            user.last_login_ip = ip
            user.save(update_fields=['last_login_ip'])
        
        # Добавляем информацию о пользователе
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
            'is_active': self.user.is_active,
        }
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        """Проверка совпадения паролей."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs
    
    def create(self, validated_data):
        """Создание нового пользователя."""
        # Удаляем подтверждение пароля из данных
        validated_data.pop('password2', None)
        
        # Извлекаем пароль
        password = validated_data.pop('password')
        
        # Создаем пользователя
        user = User.objects.create(**validated_data)
        
        # Устанавливаем пароль
        user.set_password(password)
        user.save()
        
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса сброса пароля."""
    
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения сброса пароля."""
    
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Проверка совпадения паролей."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_staff', 'created_at', 'updated_at']


class UserDetailSerializer(UserSerializer):
    """Расширенный сериализатор для детального представления пользователя."""
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['last_login_ip']
        read_only_fields = UserSerializer.Meta.read_only_fields + ['last_login_ip']


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для групп пользователей."""
    
    name = serializers.CharField(source='group.name')
    
    class Meta:
        model = ExtendedGroup
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        group_data = validated_data.pop('group', {})
        group = Group.objects.create(name=group_data.get('name', ''))
        return ExtendedGroup.objects.create(group=group, **validated_data)
    
    def update(self, instance, validated_data):
        group_data = validated_data.pop('group', {})
        if 'name' in group_data:
            instance.group.name = group_data['name']
            instance.group.save()
        return super().update(instance, validated_data)
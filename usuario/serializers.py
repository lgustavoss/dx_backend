from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'is_active', 'is_staff', 'is_superuser' , 'groups']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
            print(f"Password hash: {user.password}")  # Adicione esta linha para verificar o hash da senha
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            print(f"Password hash: {instance.password}")  # Adicione esta linha para verificar o hash da senha
        return super().update(instance, validated_data)

class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        instance = super().update(instance, validated_data)

        request_method = self.context['request'].method

        if permissions is not None:
            if request_method ==  'PUT':
                # Substituir as permissões enviadas pelas novas permissões
                instance.permissions.set(permissions)
            elif request_method == 'PATCH':
                # Adiciona as permissões enviadas às permissões existentes
                instance.permissions.add(*permissions)
        return instance

class PermissionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
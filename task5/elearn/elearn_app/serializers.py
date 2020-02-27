from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Group


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', required=False)
    email = serializers.EmailField(max_length=40, required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    last_name = serializers.CharField(allow_blank=True, max_length=30, required=True)
    date_joined = serializers.ReadOnlyField()
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    group = serializers.CharField(write_only=True, required=True)

    user_group = serializers.SerializerMethodField()   # To get "group" in serializer.data then.

    _GROUP_NAMES = tuple(str(group) for group in Group.objects.all())
    def validate_group(self, value):

        if value == "superusers":
            raise serializers.ValidationError(f"Superuser cannot be created this way.")
        elif value not in self._GROUP_NAMES:
            raise serializers.ValidationError(f"Group {value} doesn't exist.")
        else:
            return value

    def get_user_group(self, obj):
        return str(obj.groups.all()[0])

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        group_queryset = Group.objects.get(name=validated_data["group"])

        user.save()
        user.groups.set((group_queryset,))
        return user

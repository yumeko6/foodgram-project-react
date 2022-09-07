from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# from recipes.models import Recipe
# from recipes.serializers import FavouriteSerializer
# from .models import Follow
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class CurrentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


# class FollowSerializer(serializers.ModelSerializer):
#     queryset = User.objects.all()
#     user = serializers.PrimaryKeyRelatedField(queryset=queryset)
#     author = serializers.PrimaryKeyRelatedField(queryset=queryset)
#
#     class Meta:
#         model = Follow
#         fields = ('user', 'author')
#
#     def validate(self, data):
#         request = self.context.get('request')
#         author_id = data['author'].id
#         follow_exists = Follow.objects.filter(
#             user=request.user, author__id=author_id).exists()
#         if request.method == 'GET':
#             if request.user.id == author_id:
#                 raise serializers.ValidationError(
#                     {'error': 'Нельзя подписаться на самого себя!'}
#                 )
#             if follow_exists:
#                 raise serializers.ValidationError(
#                     {'error': 'Вы уже подписаны на этого автора!'}
#                 )
#         return data


# class FollowingRecipesSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')


# class FollowerSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "id",
#             "username",
#             "first_name",
#             "last_name",
#             "is_subscribed",
#             "recipes",
#             "recipes_count",
#         )
#
#     def get_is_subscribed(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Follow.objects.filter(user=user, author=obj.id).exists()
#
#     def get_recipes(self, obj):
#         recipes = obj.recipe.all()
#         return FavouriteSerializer(recipes, many=True).data
#
#     def get_recipes_count(self, obj):
#         return obj.recipe.all().count()
#
#
# class SubscriptionSerializer(serializers.ModelSerializer):
#     author = FollowerSerializer(read_only=True)
#
#     class Meta:
#         model = Follow
#         fields = ('author',)

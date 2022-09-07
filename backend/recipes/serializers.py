from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from users.models import Follow
from users.serializers import CurrentUserSerializer
from .models import (
	Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingList, Tag,
)

User = get_user_model()


class IngredientsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ingredient
		fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ('id', 'name', 'color', 'slug')


class ShowRecipeIngredientsSerializer(serializers.ModelSerializer):
	id = serializers.ReadOnlyField(source='ingredient.id')
	name = serializers.ReadOnlyField(source='ingredient.name')
	measurement_unit = serializers.ReadOnlyField(
		source='ingredient.measurement_unit'
	)

	class Meta:
		model = RecipeIngredient
		fields = ('id', 'name', 'measurement_unit', 'amount')


class ShowRecipeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Recipe
		fields = ('id', 'name', 'image', 'cooking_time')


class ShowRecipeFullSerializer(serializers.ModelSerializer):
	tags = TagsSerializer(many=True, read_only=True)
	author = CurrentUserSerializer(read_only=True)
	ingredients = serializers.SerializerMethodField()
	is_favorited = serializers.SerializerMethodField()
	is_in_shopping_cart = serializers.SerializerMethodField()

	class Meta:
		model = Recipe
		fields = (
			'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
			'cooking_time', 'is_favorited', 'is_in_shopping_cart'
		)

	def get_ingredients(self, obj):
		ingredients = RecipeIngredient.objects.filter(recipe=obj)
		return ShowRecipeIngredientsSerializer(ingredients, many=True).data

	def get_is_favorited(self, obj):
		user = self.context['request'].user
		if user.is_anonymous:
			return False
		return Favorite.objects.filter(recipe=obj, user=user).exists()

	def get_is_in_shopping_cart(self, obj):
		user = self.context['request'].user
		if user.is_anonymous:
			return False
		return ShoppingList.objects.filter(recipe=obj, user=user).exists()


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
	id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
	amount = serializers.IntegerField()

	class Meta:
		model = RecipeIngredient
		fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
	image = Base64ImageField()
	author = CurrentUserSerializer(read_only=True)
	ingredients = AddRecipeIngredientsSerializer(many=True)
	tags = serializers.PrimaryKeyRelatedField(
		queryset=Tag.objects.all(), many=True
	)
	cooking_time = serializers.IntegerField()

	class Meta:
		model = Recipe
		fields = (
			'id', 'tags', 'author', 'ingredients',
			'name', 'image', 'text', 'cooking_time'
		)

	def validate_ingredients(self, data):
		ingredients = self.initial_data.get('ingredients')
		if not ingredients:
			raise ValidationError(
				'Количество ингридиентов должно быть больше 1!'
			)
		ingredient_list = []
		for ingredient_item in ingredients:
			ingredient = get_object_or_404(
				Ingredient, id=ingredient_item['id']
			)
			if ingredient in ingredient_list:
				raise ValidationError('Ингридиенты не должны повторяться!')
			ingredient_list.append(ingredient)
			if int(ingredient_item['amount']) <= 0:
				raise ValidationError(
					'Количество ингридиента должно быть больше 0!'
				)
		return data

	def validate_tags(self, data):
		if not data:
			raise serializers.ValidationError('Добавьте тэг!')
		if len(data) != len(set(data)):
			raise serializers.ValidationError(
				'Нельзя использовать два одинаковых тэга!'
			)
		return data

	def validate_cooking_time(self, data):
		if data <= 0:
			raise ValidationError(
				'Время приготовления должно быть больше 1 минуты!'
			)
		return data

	def add_recipe_ingredients(self, ingredients, recipe):
		for ingredient in ingredients:
			ingredient_id = ingredient['id']
			amount = ingredient['amount']
			if RecipeIngredient.objects.filter(
					recipe=recipe, ingredient=ingredient_id).exists():
				amount += F('amount')
			RecipeIngredient.objects.update_or_create(
				recipe=recipe, ingredient=ingredient_id,
				defaults={'amount': amount}
			)

	def create(self, validated_data):
		author = self.context.get('request').user
		tags_data = validated_data.pop('tags')
		ingredients_data = validated_data.pop('ingredients')
		recipe = Recipe.objects.create(author=author, **validated_data)
		self.add_recipe_ingredients(ingredients_data, recipe)
		recipe.tags.set(tags_data)
		return recipe

	def update(self, recipe, validated_data):
		if 'ingredients' in self.initial_data:
			ingredients = validated_data.pop('ingredients')
			recipe.ingredients.clear()
			self.add_recipe_ingredients(ingredients, recipe)
		if 'tags' in self.initial_data:
			tags_data = validated_data.pop('tags')
			recipe.tags.set(tags_data)
		return super().update(recipe, validated_data)

	def to_representation(self, recipe):
		return ShowRecipeSerializer(
			recipe, context={'request': self.context.get('request')}).data


class FavouriteSerializer(serializers.ModelSerializer):
	recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
	user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

	class Meta:
		model = Favorite
		fields = ('user', 'recipe')

	def validate(self, data):
		user = data['user']
		recipe_id = data['recipe'].id
		if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
			raise ValidationError('Рецепт уже добавлен в избранное!')
		return data

	def to_representation(self, instance):
		request = self.context.get('request')
		context = {'request': request}
		return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
	recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
	user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

	class Meta:
		model = ShoppingList
		fields = ('user', 'recipe')

	def validate(self, data):
		user = data['user']
		recipe_id = data['recipe'].id
		if ShoppingList.objects.filter(
				user=user, recipe__id=recipe_id).exists():
			raise ValidationError('Рецепт уже добавлен в список покупок!')
		return data

	def to_representation(self, instance):
		request = self.context.get('request')
		context = {'request': request}
		return ShowRecipeSerializer(instance.recipe, context=context).data


class FollowSerializer(serializers.ModelSerializer):
	queryset = User.objects.all()
	user = serializers.PrimaryKeyRelatedField(queryset=queryset)
	author = serializers.PrimaryKeyRelatedField(queryset=queryset)

	class Meta:
		model = Follow
		fields = ('user', 'author')

	def validate(self, data):
		request = self.context.get('request')
		author_id = data['author'].id
		follow_exists = Follow.objects.filter(
			user=request.user, author__id=author_id).exists()
		if request.method == 'GET':
			if request.user.id == author_id:
				raise serializers.ValidationError(
					{'error': 'Нельзя подписаться на самого себя!'}
				)
			if follow_exists:
				raise serializers.ValidationError(
					{'error': 'Вы уже подписаны на этого автора!'}
				)
		return data


class FollowerSerializer(serializers.ModelSerializer):
	is_subscribed = serializers.SerializerMethodField()
	recipes_count = serializers.SerializerMethodField()
	recipes = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = (
			"email",
			"id",
			"username",
			"first_name",
			"last_name",
			"is_subscribed",
			"recipes",
			"recipes_count",
		)

	def get_is_subscribed(self, obj):
		user = self.context.get('request').user
		if user.is_anonymous:
			return False
		return Follow.objects.filter(user=user, author=obj.id).exists()

	def get_recipes(self, obj):
		recipes = obj.recipe.all()
		return FavouriteSerializer(recipes, many=True).data

	def get_recipes_count(self, obj):
		return obj.recipe.all().count()


class SubscriptionSerializer(serializers.ModelSerializer):
	author = FollowerSerializer(read_only=True)

	class Meta:
		model = Follow
		fields = ('author',)

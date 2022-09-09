from typing import List

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, Tag,
                            IngredientAmount, ShoppingCart)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        ingredients = data['ingredients']
        final_ingredients: List = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in final_ingredients:
                raise serializers.ValidationError(
                    {'errors': 'Ингредиенты должны быть уникальными!'}
                )
            final_ingredients.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError(
                    {'errors': 'Количество ингредиента должно быть больше 0!'}
                )

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                {'errors': 'Нужно выбрать хотя бы один тэг!'}
            )
        tags: List = []
        for tag in tags:
            if tag in tags:
                raise serializers.ValidationError(
                    {'errors': 'Тэги должны быть уникальными!'}
                )
            tags.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                {'errors': 'Время приготовления должно быть больше 0!'}
            )
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']) for ingredient in ingredients]
        )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class ShowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Этот рецепт уже в избранном!'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data

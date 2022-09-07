from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
	name = models.CharField(
		max_length=200, verbose_name='Название ингридиента'
	)
	measurement_unit = models.CharField(
		max_length=200, verbose_name='Мера ингридиента'
	)

	class Meta:
		ordering = ('name',)
		verbose_name = 'Ингридиент'
		verbose_name_plural = 'Ингридиенты'
		constraints = [
			models.UniqueConstraint(
				fields=['name', 'measurement_unit'],
				name='unique ingredient'
			)
		]

	def __str__(self):
		return self.name


class Tag(models.Model):
	ORANGE = '#FFA500'
	GREEN = '#008000'
	BLUE = '#0000FF'

	COLOR_CHOICES = [
		(ORANGE, 'Оранжевый'),
		(GREEN, 'Зеленый'),
		(BLUE, 'Синий'),
	]

	name = models.CharField(
		max_length=200, unique=True, verbose_name='Название'
	)
	color = models.CharField(
		max_length=7, unique=True, choices=COLOR_CHOICES, verbose_name='Цвет'
	)
	slug = models.CharField(max_length=200, unique=True, verbose_name='Слаг')

	class Meta:
		verbose_name = 'Тег'
		verbose_name_plural = 'Теги'

	def __str__(self):
		return self.name


class Recipe(models.Model):
	name = models.CharField(max_length=200, verbose_name='Название')
	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='recipes',
		verbose_name='Автор рецепта'
	)
	text = models.TextField(verbose_name='Описание рецепта')
	tags = models.ManyToManyField(Tag, verbose_name='Теги')
	ingredients = models.ManyToManyField(
		Ingredient, through='RecipeIngredient'
	)
	cooking_time = models.PositiveIntegerField(
		validators=[MinValueValidator(
			1, message='Время приготовления должно быть больше 1 минуты!'
		)], verbose_name='Время приготовления'
	)
	image = models.ImageField(
		upload_to='recipes/', verbose_name='Фото рецепта'
	)

	class Meta:
		ordering = ('-id',)
		verbose_name = 'Рецепт'
		verbose_name_plural = 'Рецепты'

	def __str__(self):
		return self.name


class RecipeIngredient(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(
		Ingredient, on_delete=models.PROTECT, verbose_name='Ингридиент'
	)
	amount = models.PositiveIntegerField(
		validators=[MinValueValidator(
			1, message='Количество ингридиентов должно быть больше 1!'
		)], verbose_name='Количество'
	)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Количество ингридиента'
		verbose_name_plural = 'Количество ингридиентов'
		constraints = [
			models.UniqueConstraint(
				fields=['ingredient', 'recipe'],
				name='unique ingredients recipe'
			)
		]


class Favorite(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='favorite',
		verbose_name='Пользователь'
	)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		related_name='in_favorite',
		verbose_name='Рецепт'
	)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Избранное'
		verbose_name_plural = 'Избранное'
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'recipe'],
				name='unique_favorite_recipe'
			)
		]


class ShoppingList(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='shopping_list',
		verbose_name='Пользователь'
	)
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		verbose_name='Рецепт'
	)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Список покупок'
		verbose_name_plural = 'Списки покупок'
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'recipe'],
				name='unique_shopping_list_recipe'
			)
		]

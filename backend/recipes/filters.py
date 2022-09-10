from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug', label='Tags'
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite', label='Favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping', label='Is in shopping list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_shopping(self, queryset, name, value):
        if value:
            return queryset.filter(carts__user=self.request.user)
        return queryset

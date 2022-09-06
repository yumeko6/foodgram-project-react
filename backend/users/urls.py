from django.urls import include, path

from .views import ListFollowViewSet, FollowViewSet

urlpatterns = [
    path('users/<int:id>/subscribe/', FollowViewSet,
         name='subscribe'),
    path('users/subscriptions/', ListFollowViewSet.as_view(),
         name='subscription'),
    path('', include('djoser.urls')),
]

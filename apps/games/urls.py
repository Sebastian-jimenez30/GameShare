from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, CategoryViewSet, GameCategoryViewSet, RecommendationViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'game-categories', GameCategoryViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

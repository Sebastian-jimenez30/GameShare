from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, CategoryViewSet, GameCategoryViewSet, RecommendationViewSet, ReviewViewSet
from .views import CatalogView, GameDetailView, GameCreateView, GameEditView, GameDeleteView



router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'game-categories', GameCategoryViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'reviews', ReviewViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('game/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('game/create/', GameCreateView.as_view(), name='game_create'),
    path('game/<int:pk>/edit/', GameEditView.as_view(), name='game_edit'),
    path('game/<int:pk>/delete/', GameDeleteView.as_view(), name='game_delete')

]

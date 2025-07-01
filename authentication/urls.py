from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import UserAuthViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'auth', UserAuthViewSet, basename='auth')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),

    # JWT Token refresh
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Alternative direct URLs (if needed)
    path('register/', UserAuthViewSet.as_view({'post': 'register'}), name='user-register'),
    path('login/', UserAuthViewSet.as_view({'post': 'login'}), name='user-login'),
]

from django.urls import path
from authentication.views import UserAuthViewSet

urlpatterns = [
    path('register/', UserAuthViewSet.as_view({'post': 'register'}), name='user-register'),
    path('login/', UserAuthViewSet.as_view({'post': 'login'}), name='user-login'),
]

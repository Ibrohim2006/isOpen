from django.urls import path

from authentication.views import RegisterViewSet, LoginViewSet, LogoutViewSet

urlpatterns = [
    path('register/', RegisterViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', LoginViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', LogoutViewSet.as_view({'post': 'logout'}), name='logout'),
]

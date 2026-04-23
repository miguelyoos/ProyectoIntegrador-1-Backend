from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogoutView, RegisterView, ActividadViewSet, SubtareaViewSet, EmailLoginView, VistaHoyView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'actividades', ActividadViewSet)
router.register(r'subtareas', SubtareaViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('hoy/', VistaHoyView.as_view(), name='vista_hoy'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]

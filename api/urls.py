from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogoutView
from .views import ActividadViewSet, SubtareaViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'actividades', ActividadViewSet)
router.register(r'subtareas', SubtareaViewSet)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('logout/', LogoutView.as_view(), name='logout'),
]
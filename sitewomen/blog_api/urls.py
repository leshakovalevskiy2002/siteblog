from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views import WomenAPIUpdate, WomenAPIList, WomenAPIDestroy
from .views import WomenViewSet


router = routers.DefaultRouter()
router.register(r'women', WomenViewSet, basename="posts")

urlpatterns = [
    path('women/', WomenAPIList.as_view()),
    path('women/<int:pk>/', WomenAPIUpdate.as_view()),
    path('women_delete/<int:pk>/', WomenAPIDestroy.as_view()),
    path("session_auth/", include("rest_framework.urls")),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
]
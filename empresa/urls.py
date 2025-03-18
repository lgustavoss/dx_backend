from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfiguracaoEmpresaViewSet

router = DefaultRouter()
router.register(r'configuracao', ConfiguracaoEmpresaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('consulta/cnpj/<str:cnpj>/', ConfiguracaoEmpresaViewSet.as_view({'get': 'consultar_cnpj'})),
]
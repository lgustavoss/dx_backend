from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, EstadoViewSet, CidadeViewSet, ConsultaViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'cidades', CidadeViewSet)
router.register(r'consulta', ConsultaViewSet, basename='consulta')

urlpatterns = [
    path('', include(router.urls)),
    #  Listar municipios por UF
    path('consulta/municipios/<str:uf>/', ConsultaViewSet.as_view({'get': 'municipios_por_uf'})),
    #  Consultar dados do CNPJ
    path('consulta/cnpj/<str:cnpj>/', ConsultaViewSet.as_view({'get': 'cnpj_por_numero'})),
    # Consultar dados por CEP
    path('consulta/cep/<str:cep>/', ConsultaViewSet.as_view({'get': 'cep_por_numero'})),
    # Listar estados por id
    path('consulta/estado/<int:id>/', ConsultaViewSet.as_view({'get': 'estado_por_id'})),
    # Listar municipios por id
    path('consulta/municipio/<int:id>/', ConsultaViewSet.as_view({'get': 'municipio_por_id'})),
]
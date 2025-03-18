from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from .models import Cliente, Estado, Cidade
from .serializers import ClienteSerializer, EstadoSerializer, CidadeSerializer
from .services.cnpj_service import consultar_cnpj
from .services.cep_service import consultar_cep
from .services.ibge_service import consultar_estado_por_id, consultar_municipio_por_id

class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualizar estados brasileiros
    """
    queryset = Estado.objects.all().order_by('nome')
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticated]

class CidadeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualizar cidades brasileiras, com opção de filtro por estado
    """
    queryset = Cidade.objects.all().order_by('nome')
    serializer_class = CidadeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Cidade.objects.all()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado__sigla=estado)
        return queryset

class ClienteViewSet(viewsets.ModelViewSet):
    """
    API para gerenciar clientes (CRUD completo)
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome_fantasia', 'razao_social', 'cnpj']
    
    def perform_create(self, serializer):
        """Salva o usuário atual como criador do registro"""
        serializer.save(criado_por=self.request.user, atualizado_por=self.request.user)
    
    def perform_update(self, serializer):
        """Atualiza o campo 'atualizado_por' e 'data_atualizacao' com valores atuais"""
        serializer.save(
            atualizado_por=self.request.user, 
            data_atualizacao=timezone.now()
        )

class ConsultaViewSet(ViewSet):
    """
    API para consultar dados externos (CNPJ, CEP, UFs e Municípios)
    """
    permission_classes = [IsAuthenticated]
    
    def cnpj_por_numero(self, request, cnpj):
        """
        Consulta os dados de um CNPJ usando API externa
        """
        try:
            empresa_dados = consultar_cnpj(cnpj)
            return Response(empresa_dados)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Erro ao consultar CNPJ: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def cep_por_numero(self, request, cep):
        """
        Consulta os dados de um CEP usando ViaCEP
        """
        try:
            endereco_dados = consultar_cep(cep)
            return Response(endereco_dados)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro ao consultar CEP: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['get'])
    def ufs(self, request):
        """
        Consulta todos os estados brasileiros usando a API do IBGE
        """
        try:
            url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
            response = requests.get(url)
            data = response.json()
            
            if not data:
                return Response({"error": "Nenhum estado encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            # Ordenar os estados por nome
            estados = sorted([{
                "id": estado["id"], 
                "sigla": estado["sigla"], 
                "nome": estado["nome"]
            } for estado in data], key=lambda x: x['nome'])
            
            return Response(estados)
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar estados: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def municipios_por_uf(self, request, uf):
        """
        Consulta municípios de um estado usando a API do IBGE
        """
        try:
            url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios'
            response = requests.get(url)
            data = response.json()
            
            if not data:
                return Response({"error": "Nenhum município encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            # Ordenar os municípios por nome
            municipios = sorted([{
                "id": municipio["id"], 
                "nome": municipio["nome"],
                "uf": uf
            } for municipio in data], key=lambda x: x['nome'])
            
            return Response(municipios)
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar municípios: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def estado_por_id(self, request, id):
        """
        Consulta detalhes de um estado usando seu ID do IBGE
        """
        try:
            estado_data = consultar_estado_por_id(id)
            return Response(estado_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro ao consultar estado: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def municipio_por_id(self, request, id):
        """
        Consulta detalhes de um município usando seu ID do IBGE
        """
        try:
            municipio_data = consultar_municipio_por_id(id)
            return Response(municipio_data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro ao consultar município: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
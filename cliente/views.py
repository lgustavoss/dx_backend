from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from .models import Cliente, Estado, Cidade
from .serializers import ClienteSerializer, EstadoSerializer, CidadeSerializer
import requests

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
            # Remover caracteres especiais
            cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
            
            response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj_numerico}')
            data = response.json()
            
            if 'status' in data and data['status'] == 'ERROR':
                return Response({"error": data.get('message', 'Erro na consulta do CNPJ')}, 
                            status=status.HTTP_400_BAD_REQUEST)
                
            # Mapear os dados recebidos para o formato esperado pelo nosso modelo
            empresa_dados = {
                'cnpj': data.get('cnpj', ''),
                'razao_social': data.get('nome', ''),
                'nome_fantasia': data.get('fantasia', ''),
                'endereco': f"{data.get('logradouro', '')}, {data.get('numero', '')}, {data.get('complemento', '')}".strip(','),
                'cep': data.get('cep', ''),
            }
            
            return Response(empresa_dados)
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar CNPJ: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def cep_por_numero(self, request, cep):
        """
        Consulta os dados de um CEP usando ViaCEP
        """
        try:
            # Remover caracteres especiais
            cep_numerico = ''.join(filter(str.isdigit, cep))
            
            response = requests.get(f'https://viacep.com.br/ws/{cep_numerico}/json/')
            data = response.json()
            
            if 'erro' in data:
                return Response({"error": "CEP não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            endereco_dados = {
                'endereco': data.get('logradouro', ''),
                'bairro': data.get('bairro', ''),
                'cidade': data.get('localidade', ''),
                'estado': data.get('uf', '')
            }
            
            return Response(endereco_dados)
            
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
            url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{id}'
            response = requests.get(url)
            
            if response.status_code == 404:
                return Response({"error": "Estado não encontrado"}, status=status.HTTP_404_NOT_FOUND)
                
            data = response.json()
            return Response({
                "id": data["id"],
                "sigla": data["sigla"],
                "nome": data["nome"]
            })
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar estado: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def municipio_por_id(self, request, id):
        """
        Consulta detalhes de um município usando seu ID do IBGE
        """
        try:
            url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{id}'
            response = requests.get(url)
            
            if response.status_code == 404:
                return Response({"error": "Município não encontrado"}, status=status.HTTP_404_NOT_FOUND)
                
            data = response.json()
            return Response({
                "id": data["id"],
                "nome": data["nome"],
                "estado": {
                    "id": data["microrregiao"]["mesorregiao"]["UF"]["id"],
                    "sigla": data["microrregiao"]["mesorregiao"]["UF"]["sigla"],
                    "nome": data["microrregiao"]["mesorregiao"]["UF"]["nome"]
                }
            })
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar município: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
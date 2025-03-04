from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import requests

from .models import ConfiguracaoEmpresa
from .serializers import ConfiguracaoEmpresaSerializer
from usuario.permissions import IsStaffUser

class ConfiguracaoEmpresaViewSet(viewsets.ModelViewSet):
    """
    API para gerenciar configurações da empresa.
    O sistema permite apenas uma única empresa prestadora de serviço.
    """
    queryset = ConfiguracaoEmpresa.objects.all()
    serializer_class = ConfiguracaoEmpresaSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]  # Adicionado IsStaffUser para maior controle
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescrito para permitir apenas um registro de empresa.
        Se já existir uma empresa, retorna erro.
        """
        if ConfiguracaoEmpresa.objects.exists():
            return Response(
                {"detail": "Já existe uma empresa cadastrada. Use PATCH para atualizar ou DELETE para remover."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        """
        Retorna a empresa cadastrada ou mensagem de que não existe empresa.
        """
        # Redirecionamos para o método 'atual' para padronizar a resposta
        return self.atual(request)
    
    def perform_create(self, serializer):
        """Salva o usuário atual como criador do registro"""
        serializer.save(criado_por=self.request.user, atualizado_por=self.request.user)
    
    def perform_update(self, serializer):
        """Atualiza o campo 'atualizado_por' com o usuário atual"""
        serializer.save(
            atualizado_por=self.request.user, 
            data_atualizacao=timezone.now()
        )
    
    @action(detail=False, methods=['get'])
    def atual(self, request):
        """
        Retorna as configurações atuais da empresa.
        """
        try:
            config = ConfiguracaoEmpresa.objects.first()
            if config:
                serializer = self.get_serializer(config)
                return Response(serializer.data)
            return Response({"detail": "Nenhuma configuração encontrada"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def substituir(self, request):
        """
        Substitui a configuração atual por uma nova.
        Deleta a configuração existente (se houver) e cadastra uma nova.
        """
        try:
            # Deletar configuração existente
            ConfiguracaoEmpresa.objects.all().delete()
            
            # Criar nova configuração
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao substituir configuração: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=False, methods=['get'])
    def consultar_cnpj(self, request, cnpj):
        """
        Consulta os dados de um CNPJ usando API ReceitaWS
        """
        if not cnpj:
            return Response({"error": "CNPJ não fornecido"}, status=status.HTTP_400_BAD_REQUEST)
    
        # Remover caracteres especiais
        cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
        
        try:
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
                'telefone': data.get('telefone', ''),
                'email': data.get('email', ''),
            }
            
            return Response(empresa_dados)
            
        except Exception as e:
            return Response({"error": f"Erro ao consultar CNPJ: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
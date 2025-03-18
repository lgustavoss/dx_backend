from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ConfiguracaoEmpresa
from .serializers import ConfiguracaoEmpresaSerializer
from usuario.permissions import IsStaffUser
from .services.cnpj_service import consultar_cnpj

class ConfiguracaoEmpresaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracaoEmpresa.objects.all()
    serializer_class = ConfiguracaoEmpresaSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    
    def create(self, request, *args, **kwargs):
        if ConfiguracaoEmpresa.objects.exists():
            return Response(
                {"detail": "Já existe uma empresa cadastrada. Use PATCH para atualizar ou DELETE para remover."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        return self.atual(request)
    
    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user, atualizado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(atualizado_por=self.request.user, data_atualizacao=timezone.now())
    
    @action(detail=False, methods=['get'])
    def atual(self, request):
        try:
            config = ConfiguracaoEmpresa.objects.first()
            if config:
                serializer = self.get_serializer(config)
                return Response(serializer.data)
            return Response({"detail": "Nenhuma configuração encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def substituir(self, request):
        try:
            ConfiguracaoEmpresa.objects.all().delete()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Erro ao substituir configuração: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['get'])
    def consultar_cnpj(self, request, cnpj):
        try:
            empresa_dados = consultar_cnpj(cnpj)
            return Response(empresa_dados)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Erro ao consultar CNPJ: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
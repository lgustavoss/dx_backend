from django.db import models
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ
from django.contrib.auth.models import User

class ConfiguracaoEmpresa(models.Model):
    """Modelo para armazenar configurações da empresa prestadora de serviços"""
    
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=255)
    cep = models.CharField(max_length=9)
    cidade_id = models.IntegerField()  # ID do IBGE para a cidade
    cidade_nome = models.CharField(max_length=255)  # Nome da cidade
    estado_id = models.IntegerField()  # ID do IBGE para o estado
    estado_sigla = models.CharField(max_length=2)  # Sigla do estado (SP, RJ, etc.)
    email = models.EmailField()
    telefone = models.CharField(max_length=15, blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    
    # Dados representante legal
    representante_nome = models.CharField(max_length=255)
    representante_cargo = models.CharField(max_length=100)
    representante_cpf = models.CharField(max_length=14)
    representante_rg = models.CharField(max_length=20, blank=True, null=True)
    
    # Logo da empresa
    logo = models.ImageField(upload_to='empresa/logos/', blank=True, null=True)
    
    # Campos para auditoria
    criado_por = models.ForeignKey(
        User, 
        related_name='empresas_criadas',
        on_delete=models.SET_NULL,
        null=True
    )
    atualizado_por = models.ForeignKey(
        User, 
        related_name='empresas_atualizadas',
        on_delete=models.SET_NULL,
        null=True
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.nome_fantasia
    
    def clean(self):
        # Validar CNPJ
        cnpj_numerico = ''.join(filter(str.isdigit, self.cnpj))
        validador = CNPJ()
        if not validador.validate(cnpj_numerico):
            raise ValidationError({'cnpj': 'CNPJ inválido'})
        self.cnpj = validador.mask(cnpj_numerico)
        
    class Meta:
        verbose_name = "Configuração da Empresa"
        verbose_name_plural = "Configurações da Empresa"
        db_table = 'configuracoes_empresa'
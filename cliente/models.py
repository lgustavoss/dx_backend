from django.db import models
from django.core.validators import RegexValidator

class Estado(models.Model):
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=2)

    def __str__(self):
        return self.nome

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cidades')

    def __str__(self):
        return f"{self.nome} - {self.estado.sigla}"
    
class Cliente(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]

    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cep = models.CharField(max_length=9)

    # Usar inteiros em vez de FKs para cidade e estado
    cidade_id = models.IntegerField()  # ID do IBGE para a cidade
    cidade_nome = models.CharField(max_length=255)  # Guardar o nome para conveniência
    estado_id = models.IntegerField()  # ID do IBGE para o estado
    estado_sigla = models.CharField(max_length=2)  # Sigla do estado (SP, RJ, etc.)
    
    # Dados do responsável legal
    responsavel_cpf = models.CharField(max_length=14)
    responsavel_rg = models.CharField(max_length=20)
    responsavel_nome = models.CharField(max_length=255)
    responsavel_data_nascimento = models.DateField()
    responsavel_estado_civil = models.CharField(max_length=15, choices=ESTADO_CIVIL_CHOICES)
    responsavel_email = models.EmailField()
    
    # Email financeiro
    email_financeiro = models.EmailField()

    # Campos para auditoria
    criado_por = models.ForeignKey(
        'auth.User', 
        related_name='clientes_criados',
        on_delete=models.SET_NULL,
        null=True
    )
    atualizado_por = models.ForeignKey(
        'auth.User', 
        related_name='clientes_atualizados',
        on_delete=models.SET_NULL,
        null=True
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nome_fantasia} ({self.cnpj})"
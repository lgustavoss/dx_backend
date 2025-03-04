from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from datetime import date

from .models import Estado, Cidade, Cliente
from .serializers import EstadoSerializer, CidadeSerializer, ClienteSerializer

class ModelTestCase(TestCase):
    """Testes para os modelos Estado, Cidade e Cliente"""
    
    def setUp(self):
        self.estado = Estado.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidade.objects.create(nome="São Paulo", estado=self.estado)
        self.cliente = Cliente.objects.create(
            cnpj="61.364.012/0001-06",  # CNPJ válido formatado
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            endereco="Rua Teste, 123",
            cep="01234-567",
            cidade=self.cidade,
            estado=self.estado,
            responsavel_cpf="529.982.247-25",  # CPF válido formatado
            responsavel_rg="12.345.678-9",
            responsavel_nome="João da Silva",
            responsavel_data_nascimento=date(1980, 1, 1),
            responsavel_estado_civil="casado",
            responsavel_email="joao@empresa.com",
            email_financeiro="financeiro@empresa.com"
        )
    
    def test_estado_str(self):
        """Teste para verificar a representação textual de Estado"""
        self.assertEqual(str(self.estado), "São Paulo")
    
    def test_cidade_str(self):
        """Teste para verificar a representação textual de Cidade"""
        self.assertEqual(str(self.cidade), "São Paulo - SP")
    
    def test_cliente_str(self):
        """Teste para verificar a representação textual de Cliente"""
        self.assertEqual(str(self.cliente), "Empresa Teste (61.364.012/0001-06)")

class SerializerTestCase(TestCase):
    """Testes para os serializers EstadoSerializer, CidadeSerializer e ClienteSerializer"""
    
    def setUp(self):
        self.estado = Estado.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidade.objects.create(nome="São Paulo", estado=self.estado)
        self.cliente_data = {
            "cnpj": "61364012000106",  # CNPJ válido não formatado
            "razao_social": "Empresa Teste LTDA",
            "nome_fantasia": "Empresa Teste",
            "endereco": "Rua Teste, 123",
            "cep": "01234567",
            "cidade": self.cidade.id,
            "estado": self.estado.id,
            "responsavel_cpf": "52998224725",  # CPF válido não formatado
            "responsavel_rg": "123456789",
            "responsavel_nome": "João da Silva",
            "responsavel_data_nascimento": "1980-01-01",
            "responsavel_estado_civil": "casado",
            "responsavel_email": "joao@empresa.com",
            "email_financeiro": "financeiro@empresa.com"
        }
    
    def test_estado_serializer(self):
        """Teste para validar o EstadoSerializer"""
        serializer = EstadoSerializer(instance=self.estado)
        self.assertEqual(serializer.data['nome'], "São Paulo")
        self.assertEqual(serializer.data['sigla'], "SP")
    
    def test_cidade_serializer(self):
        """Teste para validar o CidadeSerializer"""
        serializer = CidadeSerializer(instance=self.cidade)
        self.assertEqual(serializer.data['nome'], "São Paulo")
        self.assertEqual(serializer.data['estado'], self.estado.id)
    
    def test_cliente_serializer_validate_cnpj(self):
        """Teste para validar CNPJ no serializer"""
        serializer = ClienteSerializer(data=self.cliente_data)
        if not serializer.is_valid():
            print(f"Erros de validação: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['cnpj'], "61.364.012/0001-06")  # Deve estar formatado
    
    def test_cliente_serializer_validate_cpf(self):
        """Teste para validar CPF no serializer"""
        serializer = ClienteSerializer(data=self.cliente_data)
        if not serializer.is_valid():
            print(f"Erros de validação: {serializer.errors}")
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['responsavel_cpf'], "529.982.247-25")  # Deve estar formatado
    
    def test_cliente_serializer_invalid_cnpj(self):
        """Teste para validar erro com CNPJ inválido"""
        self.cliente_data['cnpj'] = "00000000000000"
        serializer = ClienteSerializer(data=self.cliente_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cnpj', serializer.errors)
    
    def test_cliente_serializer_invalid_cpf(self):
        """Teste para validar erro com CPF inválido"""
        self.cliente_data['cnpj'] = "61364012000106"  # Redefine para CNPJ válido
        self.cliente_data['responsavel_cpf'] = "00000000000"
        serializer = ClienteSerializer(data=self.cliente_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('responsavel_cpf', serializer.errors)

class ViewSetTestCase(APITestCase):
    """Testes para os viewsets EstadoViewSet, CidadeViewSet e ClienteViewSet"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Criar dados de teste
        self.estado = Estado.objects.create(nome="São Paulo", sigla="SP")
        self.cidade = Cidade.objects.create(nome="São Paulo", estado=self.estado)
        self.cliente_data = {
            "cnpj": "61364012000106",  # CNPJ válido
            "razao_social": "Empresa Teste LTDA",
            "nome_fantasia": "Empresa Teste",
            "endereco": "Rua Teste, 123",
            "cep": "01234567",
            "cidade": self.cidade.id,
            "estado": self.estado.id,
            "responsavel_cpf": "52998224725",  # CPF válido
            "responsavel_rg": "123456789",
            "responsavel_nome": "João da Silva",
            "responsavel_data_nascimento": "1980-01-01",
            "responsavel_estado_civil": "casado",
            "responsavel_email": "joao@empresa.com",
            "email_financeiro": "financeiro@empresa.com"
        }
    
    def test_estado_list(self):
        """Teste para listar estados"""
        url = reverse('estado-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar formato paginado da resposta
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cidade_list(self):
        """Teste para listar cidades"""
        url = reverse('cidade-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar formato paginado da resposta
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cidade_filter_by_estado(self):
        """Teste para filtrar cidades por estado"""
        url = f"{reverse('cidade-list')}?estado=SP"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar formato paginado da resposta
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_cliente_create(self):
        """Teste para criar um cliente"""
        url = reverse('cliente-list')
        response = self.client.post(url, self.cliente_data, format='json')
        
        # Se não for bem-sucedido, mostrar os erros para debugging
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Erros na criação: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 1)
    
    def test_cliente_list(self):
        """Teste para listar clientes"""
        # Criar um cliente primeiro
        Cliente.objects.create(
            cnpj="61.364.012/0001-06",  # CNPJ válido formatado
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            endereco="Rua Teste, 123",
            cep="01234-567",
            cidade=self.cidade,
            estado=self.estado,
            responsavel_cpf="529.982.247-25",  # CPF válido formatado
            responsavel_rg="12.345.678-9",
            responsavel_nome="João da Silva",
            responsavel_data_nascimento=date(1980, 1, 1),
            responsavel_estado_civil="casado",
            responsavel_email="joao@empresa.com",
            email_financeiro="financeiro@empresa.com"
        )
        
        url = reverse('cliente-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar formato paginado da resposta
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

class ExternalAPITestCase(APITestCase):
    """Testes para as APIs externas de consulta de CNPJ, CEP, UFs e Municípios"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
    
    @patch('cliente.views.requests.get')
    def test_consulta_cnpj(self, mock_get):
        """Teste para consulta de CNPJ"""
        # Configurar o mock para simular resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'cnpj': '61364012000106',
            'nome': 'EMPRESA TESTE LTDA',
            'fantasia': 'EMPRESA TESTE',
            'logradouro': 'RUA TESTE',
            'numero': '123',
            'complemento': 'SALA 1',
            'cep': '01234567'
        }
        mock_get.return_value = mock_response
        
        url = reverse('cliente-consulta-cnpj') + '?cnpj=61364012000106'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['razao_social'], 'EMPRESA TESTE LTDA')
        
    @patch('cliente.views.requests.get')
    def test_consulta_cep(self, mock_get):
        """Teste para consulta de CEP"""
        # Configurar o mock para simular resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'logradouro': 'Rua Teste',
            'bairro': 'Centro',
            'localidade': 'São Paulo',
            'uf': 'SP'
        }
        mock_get.return_value = mock_response
        
        url = reverse('cliente-consulta-cep') + '?cep=01234567'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cidade'], 'São Paulo')
    
    @patch('cliente.views.requests.get')
    def test_consulta_ufs(self, mock_get):
        """Teste para consulta de UFs"""
        # Configurar o mock para simular resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {'id': 35, 'sigla': 'SP', 'nome': 'São Paulo'},
            {'id': 33, 'sigla': 'RJ', 'nome': 'Rio de Janeiro'}
        ]
        mock_get.return_value = mock_response
        
        url = reverse('cliente-consulta-ufs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    @patch('cliente.views.requests.get')
    def test_consulta_municipios(self, mock_get):
        """Teste para consulta de municípios"""
        # Configurar o mock para simular resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {'id': 3550308, 'nome': 'São Paulo'},
            {'id': 3509502, 'nome': 'Campinas'}
        ]
        mock_get.return_value = mock_response
        
        url = reverse('cliente-consulta-municipios') + '?uf=SP'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
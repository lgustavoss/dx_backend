from rest_framework import serializers
from .models import Cliente, Estado, Cidade
from validate_docbr import CNPJ, CPF
import requests

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id', 'sigla', 'nome']

class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = ['id', 'nome', 'estado']

class ClienteSerializer(serializers.ModelSerializer):
    # Adicione campos virtuais para compatibilidade com o formato antigo
    cidade = serializers.IntegerField(required=False, write_only=True)
    estado = serializers.IntegerField(required=False, write_only=True)
    
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['data_criacao', 'data_atualizacao']
        # Não exigir campos que serão preenchidos no validate
        extra_kwargs = {
            'cidade_nome': {'required': False},
            'estado_sigla': {'required': False}
        }
    
    def validate_cnpj(self, value):
        # Remover caracteres não numéricos
        cnpj_numerico = ''.join(filter(str.isdigit, value))
        
        # Validar CNPJ
        validador = CNPJ()
        if not validador.validate(cnpj_numerico):
            raise serializers.ValidationError("CNPJ inválido.")
        
        # Formatar CNPJ
        return validador.mask(cnpj_numerico)
    
    def validate_responsavel_cpf(self, value):
        # Remover caracteres não numéricos
        cpf_numerico = ''.join(filter(str.isdigit, value))
        
        # Validar CPF
        validador = CPF()
        if not validador.validate(cpf_numerico):
            raise serializers.ValidationError("CPF inválido.")
        
        # Formatar CPF
        return validador.mask(cpf_numerico)
        
    def validate(self, data):
        # Mapear campos antigos para novos
        if 'cidade' in data:
            data['cidade_id'] = data.pop('cidade')
        
        if 'estado' in data:
            data['estado_id'] = data.pop('estado')
        
        # Validar se o estado existe
        try:
            estado_id = data.get('estado_id')
            if estado_id:
                url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado_id}'
                response = requests.get(url)
                if response.status_code != 200:
                    raise serializers.ValidationError({"estado_id": "Estado não encontrado"})
                estado_data = response.json()
                data['estado_sigla'] = estado_data["sigla"]
        except Exception as e:
            raise serializers.ValidationError({"estado_id": f"Erro ao validar estado: {str(e)}"})
        
        # Validar se o município existe
        try:
            cidade_id = data.get('cidade_id')
            if cidade_id:
                url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{cidade_id}'
                response = requests.get(url)
                if response.status_code != 200:
                    raise serializers.ValidationError({"cidade_id": "Município não encontrado"})
                municipio_data = response.json()
                data['cidade_nome'] = municipio_data["nome"]
        except Exception as e:
            raise serializers.ValidationError({"cidade_id": f"Erro ao validar município: {str(e)}"})
            
        return data
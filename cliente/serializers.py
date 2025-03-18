from rest_framework import serializers
from .models import Cliente, Estado, Cidade
from .validators.cnpj_validator import validar_cnpj
from .validators.cpf_validator import validar_cpf
from .services.cnpj_service import consultar_cnpj
from .services.ibge_service import consultar_estado_por_id, consultar_municipio_por_id

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
        return validar_cnpj(value)
    
    def validate_responsavel_cpf(self, value):
        return validar_cpf(value)
        
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
                estado_data = consultar_estado_por_id(estado_id)
                data['estado_sigla'] = estado_data["sigla"]
        except Exception as e:
            raise serializers.ValidationError({"estado_id": f"Erro ao validar estado: {str(e)}"})
        
        # Validar se o município existe
        try:
            cidade_id = data.get('cidade_id')
            if cidade_id:
                municipio_data = consultar_municipio_por_id(cidade_id)
                data['cidade_nome'] = municipio_data["nome"]
        except Exception as e:
            raise serializers.ValidationError({"cidade_id": f"Erro ao validar município: {str(e)}"})
            
        return data
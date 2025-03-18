from rest_framework import serializers
from .models import ConfiguracaoEmpresa
from .validators.cnpj_validator import validar_cnpj
from .services.cnpj_service import consultar_cnpj

class ConfiguracaoEmpresaSerializer(serializers.ModelSerializer):
    buscar_dados = serializers.BooleanField(default=False, write_only=True)
    
    class Meta:
        model = ConfiguracaoEmpresa
        fields = '__all__'
        read_only_fields = ['data_criacao', 'data_atualizacao', 'criado_por', 'atualizado_por']
        extra_kwargs = {
            'cidade_nome': {'required': False},
            'estado_sigla': {'required': False}
        }
        
    def validate_cnpj(self, value):
        return validar_cnpj(value)
        
    def validate(self, data):
        if data.pop('buscar_dados', False):
            cnpj = data.get('cnpj')
            if cnpj:
                try:
                    info = consultar_cnpj(cnpj)
                    data.update(info)
                except Exception as e:
                    print(f"Erro ao consultar CNPJ: {str(e)}")
                
        return data
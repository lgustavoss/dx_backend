from rest_framework import serializers
from .models import ConfiguracaoEmpresa
from validate_docbr import CNPJ
import requests

class ConfiguracaoEmpresaSerializer(serializers.ModelSerializer):
    # Campo virtual para uso na busca de CNPJ
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
        # Remover caracteres não numéricos
        cnpj_numerico = ''.join(filter(str.isdigit, value))
        
        # Validar CNPJ
        validador = CNPJ()
        if not validador.validate(cnpj_numerico):
            raise serializers.ValidationError("CNPJ inválido.")
        
        # Formatar CNPJ
        return validador.mask(cnpj_numerico)
        
    def validate(self, data):
        # Se solicitado buscar dados do CNPJ
        if data.pop('buscar_dados', False):
            cnpj = data.get('cnpj')
            if cnpj:
                try:
                    # Remover caracteres não numéricos
                    cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
                    response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj_numerico}')
                    
                    if response.status_code == 200:
                        info = response.json()
                        if 'nome' in info:
                            data['razao_social'] = info['nome']
                        if 'fantasia' in info and info['fantasia']:
                            data['nome_fantasia'] = info['fantasia']
                        if 'logradouro' in info and 'numero' in info:
                            endereco = f"{info.get('logradouro', '')}, {info.get('numero', '')}"
                            if 'complemento' in info and info['complemento']:
                                endereco += f", {info['complemento']}"
                            data['endereco'] = endereco.strip(', ')
                        if 'cep' in info:
                            data['cep'] = info['cep']
                        if 'email' in info:
                            data['email'] = info['email']
                        if 'telefone' in info:
                            data['telefone'] = info['telefone']
                except Exception as e:
                    # Log do erro, mas não impede a validação
                    print(f"Erro ao consultar CNPJ: {str(e)}")
                
        # Validar estado e cidade se fornecidos
        if 'estado_id' in data and data['estado_id']:
            try:
                url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{data["estado_id"]}'
                response = requests.get(url)
                if response.status_code == 200:
                    estado_data = response.json()
                    data['estado_sigla'] = estado_data["sigla"]
            except Exception as e:
                raise serializers.ValidationError({"estado_id": f"Erro ao validar estado: {str(e)}"})
        
        if 'cidade_id' in data and data['cidade_id']:
            try:
                url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{data["cidade_id"]}'
                response = requests.get(url)
                if response.status_code == 200:
                    municipio_data = response.json()
                    data['cidade_nome'] = municipio_data["nome"]
            except Exception as e:
                raise serializers.ValidationError({"cidade_id": f"Erro ao validar município: {str(e)}"})
                
        return data
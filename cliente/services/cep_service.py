import requests

def consultar_cep(cep):
    """
    Consulta os dados de um CEP usando API da ViaCEP
    """
    cep_numerico = ''.join(filter(str.isdigit, cep))
    response = requests.get(f'https://viacep.com.br/ws/{cep_numerico}/json/')
    data = response.json()

    if 'erro' in data:
        raise ValueError("CEP não encontrado")
    
    endereco_dados = {
        'endereco': f"{data.get('logradouro', '')}, {data.get('numero', '')}, {data.get('complemento', '')}".strip(','),
        'bairro': data.get('bairro', ''),
        'cidade': data.get('cidade', ''),
        'uf': data.get('uf', ''),
    }

    return endereco_dados
import requests

def consultar_cnpj(cnpj):
    """
    Consulta os dados de um CNPJ usando API ReceitaWS
    """
    cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
    response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj_numerico}')
    data = response.json()
    
    if 'status' in data and data['status'] == 'ERROR':
        raise ValueError(data.get('message', 'Erro na consulta do CNPJ'))
    
    empresa_dados = {
        'cnpj': data.get('cnpj', ''),
        'razao_social': data.get('nome', ''),
        'nome_fantasia': data.get('fantasia', ''),
        'endereco': f"{data.get('logradouro', '')}, {data.get('numero', '')}, {data.get('complemento', '')}".strip(','),
        'cep': data.get('cep', ''),
        'telefone': data.get('telefone', ''),
        'email': data.get('email', ''),
    }
    
    return empresa_dados
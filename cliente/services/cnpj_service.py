import requests

def consultar_cnpj(cnpj):
    """"
    Consulta os dados de um CNPJ usando API da ReceitaWS
    """
    cpnj_numerico = ''.join(filter(str.isdigit, cnpj))
    response = requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cpnj_numerico}')
    data = response.json()

    if 'status' in data and data['status'] == 'ERROR':
        raise ValueError(data.get('message', 'Erro na consulta do CNPJ'))

    empresa_dados = {
        'cnpj': data.get('cnpj', ''),
        'razao_social' = data.get('nome', ''),
        'nome_fantasia' = data.get('fantasia', ''),
        'endereco' = f"{data.get('logradouro', ''), data.get('numero', '')}, {data.get('bairro', '')}, {data.get('complemento', '')}".strip(','),
        'cep'= data.get('cep', ''),
        'municipio' = data.get('municipio', ''),
        'uf' = data.get('uf', ''),
    }

    return empresa_dados
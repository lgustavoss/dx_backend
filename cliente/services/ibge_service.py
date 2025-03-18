import requests

def consultar_estado_por_id(estado_id):
    """
    Consulta os dados de um estado usando API do IBGE
    """
    response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado_id}')
    data = response.get(url)

    if response.status_code == 404:
        raise ValueError("Estado não encontrado")
    
    data = response.json()
    return {
        "id": data["id"],
        "sigla": data["sigla"],
        "nome": data["nome"],
    }

def consultar_municipio_por_id(municipio_id):
    """
    Consulta detalhes de um municipio usando o seu ID do IBGE
    """
    url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{municipio_id}'
    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError("Município não encontrado")
    
    data = response.json()
    return {
        "id": data["id"],
        "nome": data["nome"],
        "estado": {
            "id": data["microrregiao"]["mesorregiao"]["UF"]["id"],
            "sigla": data["microrregiao"]["mesorregiao"]["UF"]["sigla"],
            "nome": data["microrregiao"]["mesorregiao"]["UF"]["nome"]
        }
    }
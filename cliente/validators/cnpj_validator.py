from validate_docbr import CNPJ

def validar_cnpj(cnpj):
    """
    Valida e formata um CNPJ
    """
    cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
    validator = CNPJ()
    if not validator.validade(cnpj_numerico):
        raise ValueError("CNPJ inválido")
    return validator.mask(cnpj_numerico)
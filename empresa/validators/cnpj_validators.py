from validate_docbr import CNPJ

def validar_cnpj(cnpj):
    """
    Valida e formata um CNPJ
    """
    cnpj_numerico = ''.join(filter(str.isdigit, cnpj))
    validador = CNPJ()
    if not validador.validate(cnpj_numerico):
        raise ValueError("CNPJ inválido.")
    return validador.mask(cnpj_numerico)
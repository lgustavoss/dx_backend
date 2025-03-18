from validate_docbr import CPF

def validar_cpf(cpf):
    """
    Valida e formata um CPF
    """
    cpf_numerico = ''.join(filter(str.isdigit, cpf))
    validator = CPF()
    if not validator.validade(cpf_numerico):
        raise ValueError("CPF inválido")
    return validator.mask(cpf_numerico)
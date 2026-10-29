import re

from django.core.exceptions import ValidationError


def calcular_dv(cuerpo):
    """Dígito verificador del RUT chileno (módulo 11)."""
    suma, multiplo = 0, 2
    for digito in reversed(str(int(cuerpo))):
        suma += int(digito) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def normalizar_rut(valor):
    """Valida un RUT y lo devuelve con formato 12.345.678-K."""
    limpio = re.sub(r'[.\-\s]', '', str(valor or '')).upper()
    if not re.fullmatch(r'\d{7,8}[\dK]', limpio):
        raise ValidationError('Ingrese un RUT válido, por ejemplo 12.345.678-5.')
    cuerpo, dv = limpio[:-1], limpio[-1]
    if calcular_dv(cuerpo) != dv:
        raise ValidationError('El dígito verificador del RUT no es válido.')
    return f"{int(cuerpo):,}".replace(',', '.') + '-' + dv


def validar_rut(valor):
    normalizar_rut(valor)

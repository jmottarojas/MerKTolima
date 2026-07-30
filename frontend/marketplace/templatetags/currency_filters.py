from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()

@register.filter
def format_cop(value):
    """
    Formatea un valor numérico como pesos colombianos.
    Ejemplo: 1500000 -> $1.500.000 COP
    """
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value)
        
        # Formatear con separadores de miles
        formatted = "{:,.0f}".format(value).replace(',', '.')
        
        return mark_safe(f"${formatted} COP")
    except (ValueError, TypeError):
        return value

@register.filter
def format_cop_simple(value):
    """
    Formatea un valor numérico como pesos colombianos sin COP.
    Ejemplo: 1500000 -> $1.500.000
    """
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value)
        
        # Formatear con separadores de miles
        formatted = "{:,.0f}".format(value).replace(',', '.')
        
        return mark_safe(f"${formatted}")
    except (ValueError, TypeError):
        return value

@register.filter
def cop_no_symbol(value):
    """
    Formatea un valor numérico con separadores de miles sin símbolo.
    Ejemplo: 1500000 -> 1.500.000
    """
    try:
        # Convertir a float si es string
        if isinstance(value, str):
            value = float(value)
        
        # Formatear con separadores de miles
        formatted = "{:,.0f}".format(value).replace(',', '.')
        
        return formatted
    except (ValueError, TypeError):
        return value
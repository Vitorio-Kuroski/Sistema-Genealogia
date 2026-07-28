"""
Módulo de validação de entradas digitadas pelo usuário no terminal.
"""

import re

TIPOS_RELACAO_VALIDOS = ('pai', 'mae', 'conjuge')


def validar_ano(mensagem):
    """Pede um ano ao usuário até que um número válido seja digitado."""
    while True:
        valor = input(mensagem)
        if valor.isdigit() and len(valor) == 4:
            return int(valor)
        print("⚠️  Digite um ano válido, com 4 dígitos (ex: 1832).")


def validar_data_nascimento(mensagem):
    """Aceita apenas ano (ex: 1800) ou data completa (ex: 1800-01-01)."""
    padrao_ano = re.compile(r'^\d{4}$')
    padrao_data = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    while True:
        valor = input(mensagem)
        if padrao_ano.match(valor):
            return f"{valor}-01-01"  # normaliza para permitir ordenação futura
        if padrao_data.match(valor):
            return valor
        print("⚠️  Use o formato AAAA ou AAAA-MM-DD (ex: 1800 ou 1800-01-01).")


def validar_tipo_relacao(mensagem):
    """Garante que o tipo de parentesco seja um dos valores aceitos."""
    while True:
        valor = input(mensagem).strip().lower()
        if valor in TIPOS_RELACAO_VALIDOS:
            return valor
        print(f"⚠️  Opções válidas: {', '.join(TIPOS_RELACAO_VALIDOS)}.")

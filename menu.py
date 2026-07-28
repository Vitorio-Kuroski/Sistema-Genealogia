"""
Módulo de interface: menu do terminal e funções que conversam com o usuário.
A lógica de banco de dados fica em banco.py; aqui só cuidamos da interação.
"""

import sqlite3

import banco
import validacao


def exibir_resultado(linha):
    """Imprime uma linha de resultado (pessoa + registro + local) formatada."""
    nome, sobrenome, data_nasc, tipo, ano_reg, cidade, paroquia, pais = linha
    print(f"Ancestral: {nome} {sobrenome} (Nasc: {data_nasc})")
    if tipo:
        print(f"Documento: {tipo} registrado em {ano_reg}")
    else:
        print("Documento: nenhum registro cadastrado ainda")
    print(f"Localidade: {cidade} - {paroquia}, {pais}")
    print("-" * 50)


def selecionar_pessoa(cursor, mensagem):
    """Busca pessoas por termo e deixa o usuário escolher uma pelo ID."""
    termo = input(mensagem).strip()
    pessoas = banco.buscar_pessoas_por_termo(cursor, termo)

    if not pessoas:
        print("Nenhuma pessoa encontrada com esse termo.")
        return None

    print("\nPessoas encontradas:")
    for id_pessoa, nome, sobrenome, data_nasc in pessoas:
        print(f"[{id_pessoa}] {nome} {sobrenome} (Nasc: {data_nasc})")

    ids_validos = {str(pessoa[0]) for pessoa in pessoas}
    while True:
        escolha = input("Digite o ID da pessoa desejada: ").strip()
        if escolha in ids_validos:
            return int(escolha)
        print("⚠️  ID inválido. Escolha um dos IDs listados acima.")


def cadastrar_dados(conexao, cursor):
    """Cadastra local, ancestral e documento histórico associados."""
    print("\n--- 1. Local ---")
    cidade = input("Digite a cidade (ex: Bobowo): ").strip()
    paroquia = input("Digite a paróquia (ex: Paróquia de Bobowo): ").strip()
    pais = input("Digite o país (ex: Polônia): ").strip()
    id_local = banco.buscar_ou_criar_local(cursor, cidade, paroquia, pais)

    print("\n--- 2. Ancestral ---")
    nome = input("Digite o nome do ancestral: ").strip()
    sobrenome = input("Digite o sobrenome: ").strip()
    data_nascimento = validacao.validar_data_nascimento(
        "Digite a data ou ano de nascimento (ex: 1800-01-01 ou 1800): ")
    id_pessoa = banco.inserir_pessoa(cursor, nome, sobrenome, data_nascimento, id_local)

    print("\n--- 3. Documento Histórico ---")
    tipo_registro = input("Qual o tipo de registro? (ex: Batismo, Matrimônio, Óbito): ").strip()
    ano_registro = validacao.validar_ano("Ano em que o registro foi feito: ")
    link = input("Link de referência ou nome do arquivo original: ").strip()

    try:
        banco.inserir_registro(cursor, id_pessoa, tipo_registro, ano_registro, link)
        conexao.commit()
        print("\n✅ Registro cadastrado com sucesso!")
    except sqlite3.Error as erro:
        conexao.rollback()
        print(f"\n❌ Erro ao salvar o registro: {erro}")


def consultar_dados(cursor):
    """Lista todos os registros, incluindo pessoas sem documentos vinculados."""
    print("\n=============== RELATÓRIO DO BANCO DE DADOS ===============")
    resultados = banco.consultar_todos(cursor)

    if not resultados:
        print("Nenhum registro encontrado no banco de dados ainda.")
    else:
        for linha in resultados:
            exibir_resultado(linha)
    print("===========================================================\n")


def buscar_por_nome(cursor):
    """Busca ancestrais por nome ou sobrenome (busca parcial)."""
    termo = input("\nDigite o nome ou sobrenome para buscar: ").strip()
    resultados = banco.consultar_por_termo(cursor, termo)

    print(f"\n=========== RESULTADOS PARA '{termo}' ===========")
    if not resultados:
        print("Nenhum ancestral encontrado com esse nome.")
    else:
        for linha in resultados:
            exibir_resultado(linha)
    print("===================================================\n")


def cadastrar_parentesco(conexao, cursor):
    """Liga duas pessoas já cadastradas por uma relação de parentesco."""
    print("\n--- Cadastro de Parentesco ---")

    id_pessoa = selecionar_pessoa(cursor, "Buscar a pessoa (nome ou sobrenome): ")
    if id_pessoa is None:
        return

    id_parente = selecionar_pessoa(cursor, "Buscar o parente dessa pessoa (nome ou sobrenome): ")
    if id_parente is None:
        return

    if id_pessoa == id_parente:
        print("⚠️  Uma pessoa não pode ser parente dela mesma.")
        return

    tipo_relacao = validacao.validar_tipo_relacao(
        "Qual a relação do parente com a pessoa? (pai, mae, conjuge): ")

    try:
        banco.inserir_parentesco(cursor, id_pessoa, id_parente, tipo_relacao)
        conexao.commit()
        print("\n✅ Parentesco cadastrado com sucesso!")
    except sqlite3.Error as erro:
        conexao.rollback()
        print(f"\n❌ Erro ao salvar o parentesco: {erro}")


def ver_parentes(cursor):
    """Mostra os parentes cadastrados de uma pessoa."""
    id_pessoa = selecionar_pessoa(cursor, "\nBuscar a pessoa (nome ou sobrenome): ")
    if id_pessoa is None:
        return

    parentes = banco.buscar_parentes(cursor, id_pessoa)

    print("\n=============== PARENTES ===============")
    if not parentes:
        print("Nenhum parentesco cadastrado para essa pessoa.")
    else:
        for tipo_relacao, nome, sobrenome in parentes:
            print(f"{tipo_relacao.capitalize()}: {nome} {sobrenome}")
    print("==========================================\n")


def menu_principal():
    """Função que gerencia o loop do programa."""
    conexao, cursor = banco.conectar_banco()

    try:
        while True:
            print("\n+++ SISTEMA DE GENEALOGIA +++")
            print("1. Cadastrar novo registro")
            print("2. Visualizar relatório completo")
            print("3. Buscar por nome ou sobrenome")
            print("4. Cadastrar parentesco")
            print("5. Ver parentes de uma pessoa")
            print("6. Sair")

            opcao = input("Escolha uma opção (1 a 6): ")

            if opcao == '1':
                cadastrar_dados(conexao, cursor)
            elif opcao == '2':
                consultar_dados(cursor)
            elif opcao == '3':
                buscar_por_nome(cursor)
            elif opcao == '4':
                cadastrar_parentesco(conexao, cursor)
            elif opcao == '5':
                ver_parentes(cursor)
            elif opcao == '6':
                print("Encerrando o sistema...")
                break
            else:
                print("Opção inválida. Tente novamente.")
    finally:
        conexao.close()

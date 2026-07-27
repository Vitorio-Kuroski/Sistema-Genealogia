import sqlite3
import re


def conectar_banco():
    """Conecta ao banco de dados e cria as tabelas se não existirem."""
    conexao = sqlite3.connect('dados_familia.db')
    cursor = conexao.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Locais (
        id_local INTEGER PRIMARY KEY AUTOINCREMENT,
        cidade VARCHAR(100),
        paroquia VARCHAR(100),
        pais VARCHAR(50)
    );

    CREATE TABLE IF NOT EXISTS Pessoas (
        id_pessoa INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(50),
        sobrenome VARCHAR(50),
        data_nascimento DATE,
        id_local_nascimento INTEGER,
        FOREIGN KEY (id_local_nascimento) REFERENCES Locais(id_local)
    );

    CREATE TABLE IF NOT EXISTS Registros (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pessoa INTEGER,
        tipo_registro VARCHAR(50),
        ano_registro INTEGER,
        documento_original_link TEXT,
        FOREIGN KEY (id_pessoa) REFERENCES Pessoas(id_pessoa)
    );
    ''')
    return conexao, cursor


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


def buscar_ou_criar_local(cursor, cidade, paroquia, pais):
    """Reaproveita um local já cadastrado em vez de duplicar."""
    cursor.execute('''
        SELECT id_local FROM Locais
        WHERE cidade = ? AND paroquia = ? AND pais = ?
    ''', (cidade, paroquia, pais))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    cursor.execute("INSERT INTO Locais (cidade, paroquia, pais) VALUES (?, ?, ?)",
                   (cidade, paroquia, pais))
    return cursor.lastrowid


def cadastrar_dados(conexao, cursor):
    """Função para receber os dados do usuário via terminal."""
    print("\n--- 1. Local ---")
    cidade = input("Digite a cidade (ex: Bobowo): ").strip()
    paroquia = input("Digite a paróquia (ex: Paróquia de Bobowo): ").strip()
    pais = input("Digite o país (ex: Polônia): ").strip()

    id_local = buscar_ou_criar_local(cursor, cidade, paroquia, pais)

    print("\n--- 2. Ancestral ---")
    nome = input("Digite o nome do ancestral: ").strip()
    sobrenome = input("Digite o sobrenome: ").strip()
    data_nascimento = validar_data_nascimento(
        "Digite a data ou ano de nascimento (ex: 1800-01-01 ou 1800): ")

    cursor.execute("INSERT INTO Pessoas (nome, sobrenome, data_nascimento, id_local_nascimento) VALUES (?, ?, ?, ?)",
                   (nome, sobrenome, data_nascimento, id_local))
    id_pessoa = cursor.lastrowid

    print("\n--- 3. Documento Histórico ---")
    tipo_registro = input("Qual o tipo de registro? (ex: Batismo, Matrimônio, Óbito): ").strip()
    ano_registro = validar_ano("Ano em que o registro foi feito: ")
    link = input("Link de referência ou nome do arquivo original: ").strip()

    try:
        cursor.execute("INSERT INTO Registros (id_pessoa, tipo_registro, ano_registro, documento_original_link) VALUES (?, ?, ?, ?)",
                       (id_pessoa, tipo_registro, ano_registro, link))
        conexao.commit()
        print("\n✅ Registro cadastrado com sucesso!")
    except sqlite3.Error as erro:
        conexao.rollback()
        print(f"\n❌ Erro ao salvar o registro: {erro}")


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


def consultar_dados(cursor):
    """Lista todos os registros, incluindo pessoas sem documentos vinculados."""
    print("\n=============== RELATÓRIO DO BANCO DE DADOS ===============")
    cursor.execute('''
        SELECT Pessoas.nome, Pessoas.sobrenome, Pessoas.data_nascimento,
               Registros.tipo_registro, Registros.ano_registro,
               Locais.cidade, Locais.paroquia, Locais.pais
        FROM Pessoas
        LEFT JOIN Registros ON Pessoas.id_pessoa = Registros.id_pessoa
        JOIN Locais ON Pessoas.id_local_nascimento = Locais.id_local
    ''')

    resultados = cursor.fetchall()

    if not resultados:
        print("Nenhum registro encontrado no banco de dados ainda.")
    else:
        for linha in resultados:
            exibir_resultado(linha)
    print("===========================================================\n")


def buscar_por_nome(cursor):
    """Busca ancestrais por nome ou sobrenome (busca parcial)."""
    termo = input("\nDigite o nome ou sobrenome para buscar: ").strip()

    cursor.execute('''
        SELECT Pessoas.nome, Pessoas.sobrenome, Pessoas.data_nascimento,
               Registros.tipo_registro, Registros.ano_registro,
               Locais.cidade, Locais.paroquia, Locais.pais
        FROM Pessoas
        LEFT JOIN Registros ON Pessoas.id_pessoa = Registros.id_pessoa
        JOIN Locais ON Pessoas.id_local_nascimento = Locais.id_local
        WHERE Pessoas.nome LIKE ? OR Pessoas.sobrenome LIKE ?
    ''', (f"%{termo}%", f"%{termo}%"))

    resultados = cursor.fetchall()

    print(f"\n=========== RESULTADOS PARA '{termo}' ===========")
    if not resultados:
        print("Nenhum ancestral encontrado com esse nome.")
    else:
        for linha in resultados:
            exibir_resultado(linha)
    print("===================================================\n")


def menu_principal():
    """Função que gerencia o loop do programa."""
    conexao, cursor = conectar_banco()

    try:
        while True:
            print("\n+++ SISTEMA DE GENEALOGIA +++")
            print("1. Cadastrar novo registro")
            print("2. Visualizar relatório completo")
            print("3. Buscar por nome ou sobrenome")
            print("4. Sair")

            opcao = input("Escolha uma opção (1 a 4): ")

            if opcao == '1':
                cadastrar_dados(conexao, cursor)
            elif opcao == '2':
                consultar_dados(cursor)
            elif opcao == '3':
                buscar_por_nome(cursor)
            elif opcao == '4':
                print("Encerrando o sistema...")
                break
            else:
                print("Opção inválida. Tente novamente.")
    finally:
        conexao.close()


# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()

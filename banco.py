"""
Módulo de acesso ao banco de dados.

Concentra toda a comunicação com o SQLite: criação das tabelas,
inserções e consultas usadas pelo sistema de genealogia. Nenhuma
função aqui interage diretamente com o usuário (isso fica em menu.py).
"""

import sqlite3


def conectar_banco():
    """Conecta ao banco de dados e cria as tabelas se não existirem."""
    conexao = sqlite3.connect('dados_familia.db')
    cursor = conexao.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Locais (
        id_local INTEGER PRIMARY KEY AUTOINCREMENT,
        cidade VARCHAR(100) COLLATE NOCASE,
        paroquia VARCHAR(100) COLLATE NOCASE,
        pais VARCHAR(50) COLLATE NOCASE
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

    CREATE TABLE IF NOT EXISTS Parentescos (
        id_parentesco INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pessoa INTEGER,
        id_parente INTEGER,
        tipo_relacao VARCHAR(20),
        FOREIGN KEY (id_pessoa) REFERENCES Pessoas(id_pessoa),
        FOREIGN KEY (id_parente) REFERENCES Pessoas(id_pessoa)
    );
    ''')
    return conexao, cursor


# ---------- Locais ----------

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


# ---------- Pessoas ----------

def inserir_pessoa(cursor, nome, sobrenome, data_nascimento, id_local):
    cursor.execute('''
        INSERT INTO Pessoas (nome, sobrenome, data_nascimento, id_local_nascimento)
        VALUES (?, ?, ?, ?)
    ''', (nome, sobrenome, data_nascimento, id_local))
    return cursor.lastrowid


def buscar_pessoas_por_termo(cursor, termo):
    """Busca pessoas por nome ou sobrenome (busca parcial)."""
    cursor.execute('''
        SELECT id_pessoa, nome, sobrenome, data_nascimento
        FROM Pessoas
        WHERE nome LIKE ? OR sobrenome LIKE ?
    ''', (f"%{termo}%", f"%{termo}%"))
    return cursor.fetchall()


# ---------- Registros ----------

def inserir_registro(cursor, id_pessoa, tipo_registro, ano_registro, link):
    cursor.execute('''
        INSERT INTO Registros (id_pessoa, tipo_registro, ano_registro, documento_original_link)
        VALUES (?, ?, ?, ?)
    ''', (id_pessoa, tipo_registro, ano_registro, link))


def consultar_todos(cursor):
    """Retorna todas as pessoas com seus registros e locais (mesmo sem documento)."""
    cursor.execute('''
        SELECT Pessoas.nome, Pessoas.sobrenome, Pessoas.data_nascimento,
               Registros.tipo_registro, Registros.ano_registro,
               Locais.cidade, Locais.paroquia, Locais.pais
        FROM Pessoas
        LEFT JOIN Registros ON Pessoas.id_pessoa = Registros.id_pessoa
        JOIN Locais ON Pessoas.id_local_nascimento = Locais.id_local
    ''')
    return cursor.fetchall()


def consultar_por_termo(cursor, termo):
    """Mesmo relatório de consultar_todos, filtrado por nome ou sobrenome."""
    cursor.execute('''
        SELECT Pessoas.nome, Pessoas.sobrenome, Pessoas.data_nascimento,
               Registros.tipo_registro, Registros.ano_registro,
               Locais.cidade, Locais.paroquia, Locais.pais
        FROM Pessoas
        LEFT JOIN Registros ON Pessoas.id_pessoa = Registros.id_pessoa
        JOIN Locais ON Pessoas.id_local_nascimento = Locais.id_local
        WHERE Pessoas.nome LIKE ? OR Pessoas.sobrenome LIKE ?
    ''', (f"%{termo}%", f"%{termo}%"))
    return cursor.fetchall()


# ---------- Parentescos ----------

def inserir_parentesco(cursor, id_pessoa, id_parente, tipo_relacao):
    """
    Registra que 'id_parente' é {tipo_relacao} de 'id_pessoa'.
    Cônjuge é uma relação simétrica, então é registrada nos dois sentidos.
    """
    cursor.execute('''
        INSERT INTO Parentescos (id_pessoa, id_parente, tipo_relacao)
        VALUES (?, ?, ?)
    ''', (id_pessoa, id_parente, tipo_relacao))

    if tipo_relacao == 'conjuge':
        cursor.execute('''
            INSERT INTO Parentescos (id_pessoa, id_parente, tipo_relacao)
            VALUES (?, ?, ?)
        ''', (id_parente, id_pessoa, tipo_relacao))


def buscar_parentes(cursor, id_pessoa):
    """Retorna a lista de parentes de uma pessoa: (tipo_relacao, nome, sobrenome)."""
    parentes = []

    # relações em que a pessoa é o "ponto de partida" (pai, mãe, cônjuge)
    cursor.execute('''
        SELECT Parentescos.tipo_relacao, Pessoas.nome, Pessoas.sobrenome
        FROM Parentescos
        JOIN Pessoas ON Parentescos.id_parente = Pessoas.id_pessoa
        WHERE Parentescos.id_pessoa = ?
    ''', (id_pessoa,))
    parentes.extend(cursor.fetchall())

    # relações em que a pessoa aparece como pai/mãe de outra (ou seja, é um filho)
    cursor.execute('''
        SELECT Pessoas.nome, Pessoas.sobrenome
        FROM Parentescos
        JOIN Pessoas ON Parentescos.id_pessoa = Pessoas.id_pessoa
        WHERE Parentescos.id_parente = ? AND Parentescos.tipo_relacao IN ('pai', 'mae')
    ''', (id_pessoa,))
    parentes.extend(('filho(a)', nome, sobrenome) for nome, sobrenome in cursor.fetchall())

    return parentes

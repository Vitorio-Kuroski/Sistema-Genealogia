# Sistema de Genealogia

Programa de terminal pra organizar pesquisa genealógica: pessoas, onde nasceram, documentos históricos que comprovam isso (batismo, matrimônio, óbito) e como as pessoas cadastradas se relacionam entre si (pai, mãe, cônjuge).

Comecei com tudo em um arquivo só, mas separei em módulos pra ficar mais fácil de mexer.

## Arquivos

- `main.py` — é o que você roda
- `menu.py` — o menu e as perguntas que aparecem no terminal
- `banco.py` — conversa com o SQLite (criação das tabelas, inserts, selects)
- `validacao.py` — confere se o que a pessoa digitou faz sentido (ano, data, tipo de relação)

Precisa manter os quatro na mesma pasta.

## Rodando

Só precisa de Python 3, o `sqlite3` já vem junto.

```
python main.py
```

Na primeira vez que rodar, ele cria o `dados_familia.db` sozinho, na mesma pasta.

## O que dá pra fazer

1. Cadastrar novo registro (local + pessoa + documento)
2. Ver relatório com tudo que já foi cadastrado
3. Buscar por nome ou sobrenome
4. Cadastrar parentesco entre duas pessoas já cadastradas
5. Ver os parentes de uma pessoa
6. Sair

## Detalhes que vale saber

- Data de nascimento pode ser só o ano (`1800`) ou completa (`1800-01-01`).
- Se você cadastrar duas pessoas do mesmo lugar (mesma cidade/paróquia/país), ele reaproveita o local em vez de duplicar.
- Cônjuge é dos dois lados: se cadastrar A como cônjuge de B, B já aparece automaticamente como cônjuge de A.

## Ainda falta

- Editar ou excluir registros
- Exportar relatório pra PDF/CSV

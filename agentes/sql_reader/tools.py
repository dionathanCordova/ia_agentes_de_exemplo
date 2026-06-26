from decimal import Decimal

from .db_connector import get_connection


def _serialize_row(row: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


def run_query(sql: str) -> list[dict]:
    """Executa uma consulta SQL (SELECT) no banco e retorna as linhas.

    Args:
        sql: Comando SQL de leitura a ser executado.

    Returns:
        Lista de dicionarios representando as linhas retornadas.
    """
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Apenas comandos SELECT sao permitidos em run_query.")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return [_serialize_row(row) for row in rows]


def describe_database() -> dict[str, list[dict]]:
    """Retorna o schema completo do banco: tabelas e suas colunas.

    Returns:
        Dicionario {nome_tabela: lista de colunas (Field, Type, Null, Key, Default, Extra)}.
    """
    conn = get_connection()
    tables_cursor = conn.cursor()
    tables_cursor.execute("SHOW TABLES")
    tables = [row[0] for row in tables_cursor.fetchall()]
    tables_cursor.close()

    schema = {}
    desc_cursor = conn.cursor(dictionary=True)
    for table in tables:
        desc_cursor.execute(f"DESCRIBE {table}")
        schema[table] = desc_cursor.fetchall()
    desc_cursor.close()
    return schema

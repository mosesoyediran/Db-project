from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from os import environ as env

load_dotenv()


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None


    def open(self, url=None):
        if not url:
            url = env.get("CONNECTION_URL")

        self.conn = connect(url)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        

    def close(self):
        self.cursor.close()
        self.conn.close()
        
        

    @staticmethod
    def _compose_kv_and(separator=" AND ", kv_pairs=None):
        return sql.SQL(separator).join(
            sql.SQL("{} = {}").format(
                sql.Identifier(k), sql.Literal(v)) for k, v in kv_pairs
        )

    def write(self,
              table: str,
              columns: list[str],
              data: list):
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table),
            sql.SQL(",").join(map(sql.Identifier, columns)),
            sql.SQL(",").join(map(sql.Literal, data)),
        )

        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchone().get('id')

    def get(self,
            table: str,
            columns: list[str],
            limit: int = None,
            where: dict = None,
            or_where: dict = None,
            contains: dict = None
            ):

        query = sql.SQL("SELECT {} FROM {}").format(
            sql.SQL(',').join(map(sql.Identifier, columns)),
            sql.Identifier(table)
        )

        if contains:
            query += sql.SQL(" WHERE {}").format(
                sql.SQL(" OR ").join(
                    sql.SQL("{} LIKE {}").format(
                        sql.Identifier(k),
                        sql.Literal(f"%{v}%")
                    ) for k, v in contains.items()
                ))

        if where:
            starter = sql.SQL(" WHERE ({})")

            if contains:
                if or_where:
                    starter = sql.SQL(" AND (({})")
                else:
                    starter = sql.SQL(" AND ({})")

            query += starter.format(
                self._compose_kv_and(kv_pairs=where.items())
            )

        if where and or_where:
            query += sql.SQL(" OR ({})").format(
                self._compose_kv_and(kv_pairs=or_where.items())
            )

            if contains:
                query += sql.SQL(")")

        if limit:
            query += sql.SQL(" LIMIT {}").format(sql.Literal(limit))

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_one(self,
                table: str,
                columns: list[str],
                where: dict = None):
        result = self.get(table, columns, 1, where)  # [{}]
        if len(result):
            return result[0]  # {}

    # ...WHERE col1 like '%search%' OR col2 like '%search%'
    def get_contains(self,
                     table: str,
                     columns: list[str],
                     search: str,
                     limit: int = None):
        query = sql.SQL("SELECT {} FROM {} WHERE {}").format(
            sql.SQL(',').join(map(sql.Identifier, columns)),
            sql.Identifier(table),
            sql.SQL(" OR ").join(
                sql.SQL("{} LIKE {}").format(
                    sql.Identifier(k), sql.Literal(f"%{search}%")) for k in columns
            )
        )

        if limit:
            query += sql.SQL(" LIMIT {}").format(sql.Literal(limit))

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update(self,
               table: str,
               columns: list[str],
               data: list,
               where: dict = None):
        where_clause = sql.SQL("")

        if where:
            where_clause = sql.SQL("WHERE {}").format(
                self._compose_kv_and(kv_pairs=where.items())
            )

        query = sql.SQL("UPDATE {} SET {} {}").format(
            sql.Identifier(table),
            self._compose_kv_and(separator=",", kv_pairs=zip(columns, data)),
            where_clause
        )

        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.rowcount

    def delete(self,
               table: str,
               where: dict = None):
        where_clause = sql.SQL("")

        if where:
            where_clause = sql.SQL("WHERE {}").format(
                self._compose_kv_and(kv_pairs=where.items())
            )

        query = sql.SQL("DELETE FROM {} {}").format(
            sql.Identifier(table),
            where_clause
        )

        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.rowcount

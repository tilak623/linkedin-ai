import unittest

from backend.app.core.db import Database, _PostgreSQLConnection, _postgres_placeholders


class TestPostgreSQLSupport(unittest.TestCase):
    def test_placeholder_conversion_skips_quoted_question_marks(self):
        query = """SELECT ?, '?' AS literal, "?" AS identifier, 'it''s ?' AS escaped"""

        self.assertEqual(
            _postgres_placeholders(query),
            """SELECT %s, '?' AS literal, "?" AS identifier, 'it''s ?' AS escaped""",
        )

    def test_connection_adapts_begin_and_boolean_parameters(self):
        class FakeConnection:
            query = None
            params = None

            def execute(self, query, params):
                self.query = query
                self.params = params
                return "cursor"

        connection = FakeConnection()
        adapter = _PostgreSQLConnection(connection)

        self.assertEqual(adapter.execute("BEGIN IMMEDIATE"), "cursor")
        self.assertEqual(connection.query, "BEGIN")
        self.assertEqual(adapter.execute("UPDATE flags SET enabled = ?", (True,)), "cursor")
        self.assertEqual(connection.query, "UPDATE flags SET enabled = %s")
        self.assertEqual(connection.params, (1,))

    def test_database_reports_postgresql_driver_for_postgres_urls(self):
        database = Database(database_url="postgres://user:password@localhost/database")

        self.assertEqual(database.driver_name, "postgresql")
        self.assertTrue(database.uses_postgres)


if __name__ == "__main__":
    unittest.main()

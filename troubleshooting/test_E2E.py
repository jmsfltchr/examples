import unittest

from grakn.client import GraknClient
from migration import migrate
from troubleshooting import troubleshoot

KEYSPACE = "troubleshooting"


class TestE2E (unittest.TestCase):
    def test_app_runs_e2e(self):
        migrate(KEYSPACE)
        troubleshoot(KEYSPACE)

    def tearDown(self):
        with GraknClient(uri="localhost:48555") as client:
            client.keyspaces().delete(KEYSPACE)
        print("Deleted the troubleshooting keyspace")


if __name__ == '__main__':
    unittest.main()

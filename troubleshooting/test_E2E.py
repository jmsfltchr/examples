import unittest

from grakn.client import GraknClient
from migration import migrate
from app import Troubleshooter

KEYSPACE = "troubleshooting"


class TestE2E (unittest.TestCase):
    def test_app_runs_e2e(self):
        migrate(KEYSPACE, schema_path='../schemas/troubleshooting-schema.gql')
        ts = Troubleshooter(0)
        ts.troubleshoot()
        ts.respond("Somewhat")
        ts.respond("Faint and distorted")
        ts.exit()

    def test_migration_spot_check(self):
        migrate(KEYSPACE)
        with GraknClient(uri="localhost:48555") as client:
            with client.session(keyspace=KEYSPACE) as session:
                with session.transaction().write() as tx:
                    answers = list(tx.query("""
                    match
                    $flt isa fault, has name "poor connection";
                    $ques isa question, has name "audible to others";
                    $ques has response-option $res0;
                    $res0 "Somewhat";
                    $ques has response-option $res1;
                    $res1 "Not at all";
                    (
                        indicating-response: $res0,
                        indicating-response: $res1,
                        identified-fault: $flt,
                        identifying-question: $ques
                    ) isa fault-identification; get;
                    """))
                    self.assertEqual(1, len(answers))

    def tearDown(self):
        with GraknClient(uri="localhost:48555") as client:
            client.keyspaces().delete(KEYSPACE)
        print("Deleted the troubleshooting keyspace")


if __name__ == '__main__':
    unittest.main()

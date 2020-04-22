import unittest

from grakn.client import GraknClient
from migration import migrate
from app import Troubleshooter

KEYSPACE = "troubleshooting"


class TestE2E (unittest.TestCase):
    def test_app_runs_e2e(self):
        migrate(KEYSPACE, schema_path='../schemas/troubleshooting-schema.gql')
        for i in range(0, 100):
            print(f"iteration {i}")
            ts = Troubleshooter(i)
            # ts = Troubleshooter(0)
            ts.troubleshoot()
            ts.respond("Somewhat")
            fault_names = ts.respond("Faint and distorted")
            ts.exit()

            expected_fault_names = {"poor connection", "wrong mic connected", "low input volume"}

            self.assertSetEqual(expected_fault_names, fault_names)

    def test_migration_spot_check(self):
        migrate(KEYSPACE)
        question_name = "audible to others"

        with GraknClient(uri="localhost:48555") as client:
            with client.session(keyspace=KEYSPACE) as session:
                with session.transaction().write() as tx:
                    tx.query(f"""
                    match
                        $ques isa question, has name "{question_name}",
                            has response-option $opt;
                            $opt "Somewhat";
                        $ts isa troubleshooting-session, has identifier 0;
                    insert
                        (parent-session: $ts, response: $opt, considered-question: $ques) isa user-response;
                    """)
                    tx.commit()

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

    def test_non_determinism(self):
        migrate(KEYSPACE, schema_path='../schemas/troubleshooting-schema.gql')
        with GraknClient(uri="localhost:48555") as client:
            with client.session(keyspace=KEYSPACE) as session:
                with session.transaction().write() as tx:
                    tx.query(f"match $ts isa troubleshooting-session, "
                                         f"has identifier 0; get;")
                    tx.query(f"""
                    match 
                        $u isa user, has identifier 0;
                    insert 
                        $ts isa troubleshooting-session, has identifier 0; 
                        (session-owner: $u, owned-session: $ts) isa session-ownership;
                    """)
                    tx.commit()

                with session.transaction().write() as tx:
                    tx.query(f"""
                    match
                        $ques isa question, has name "audible to others",
                            has response-option $opt;
                            $opt "Somewhat";
                        $ts isa troubleshooting-session, has identifier 0;
                    insert
                        (parent-session: $ts, response: $opt, considered-question: $ques) isa user-response;
                    """)
                    tx.commit()

                with session.transaction().write() as tx:
                    answers = list(tx.query(f"""
                    match
                        (diagnosed-fault: $flt, parent-session: $ts) isa diagnosis;
                        $ts isa troubleshooting-session, has identifier 0; 
                        $flt has name $flt-name;
                        $s($flt, $proc) isa solution;
                        $proc isa procedure, has name $proc-name, has description $proc-desc;
                    get $flt-name, $proc-name, $proc-desc; group $flt-name;
                    """))
                    print(len(answers))

                    list(tx.query(f"""
                    match
                        (diagnosed-fault: $flt, parent-session: $ts) isa diagnosis;
                    get;
                    """))
                    print(len(answers))

                    list(tx.query(f"""
                    match
                        (diagnosed-fault: $flt, parent-session: $ts) isa diagnosis;
                        $ts isa troubleshooting-session, has identifier 0; 
                        $flt has name $flt-name;
                        $s($flt, $proc) isa solution;
                        $proc isa procedure, has name $proc-name, has description $proc-desc;
                    get $flt-name, $proc-name, $proc-desc; group $flt-name;
                    """))
                    print(len(answers))

    def tearDown(self):
        with GraknClient(uri="localhost:48555") as client:
            client.keyspaces().delete(KEYSPACE)
        print("Deleted the troubleshooting keyspace")


if __name__ == '__main__':
    unittest.main()

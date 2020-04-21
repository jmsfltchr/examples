from grakn.client import GraknClient


def troubleshoot(keyspace_name):
    """
    Run a short demo of how a troubleshooting session can work
    Using templates for these queries would be wise, but I want to demonstrate how this works in an easy-to-read way
    :return:
    """
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace=keyspace_name) as session:
            with session.transaction().write() as tx:

                session_id = 10
                user_id = 0

                # Proposed workflow:
                tx.query(f"""
                match 
                    $u isa user, has identifier {user_id};
                insert 
                    $ts isa troubleshooting-session, has identifier {session_id}; 
                    (session-owner: $u, owned-session: $ts) isa session-ownership;
                """)

                # Find out the product the user is asking about
                tx.query(f"""
                match 
                    (owned-product: $p, product-owner: $u) isa product-ownership; 
                    $p isa product, has name $n; 
                get $n;
                """)

                # Each iteration, query for a fully identified fault (where all of the user's responses match the
                # criteria for this fault
                answers = list(tx.query(f"""
                match
                    (diagnosed-fault: $flt, parent-session: $ts) isa diagnosis;
                    $ts isa troubleshooting-session, has identifier {session_id}; $flt has name $n;
                get $n;
                """))

                if len(answers) > 0:
                    # in this case there is a solution, then query for its solution (or part of the same query)
                    print(f"Fault is {answers[0].get('n').value()}")
                else:
                    # Else, query to find the question to ask which will eliminate the most failure scenarios:
                    answers = list(tx.query(f"""
                    match
                        (diagnosed-fault: $flt, parent-session: $ts) isa candidate-diagnosis;
                        (question-not-asked: $ques, parent-session: $ts) isa unasked-question;
                        ($flt, $ques) isa fault-identification; $ques has text $qu-text;
                    get $qu-text, $flt; group $qu-text; count;
                    """))
                    print(answers)

                    # Pick the question with the highest score and ask the user to pick the positive or negative response:
                    question_name = "audible to all"
                    tx.query(f"""
                    match 
                        $ques isa question, 
                            has name "{question_name}", 
                            has response-option $res; 
                    get $res;
                    """)
                    # You can make this more fancy by using some NLP wizardry to interpret their response and map ot to one of the available responses

                    # insert their response and repeat, here it's positive:
                    tx.query(f"""
                    match
                        $ques isa question, has name "{question_name}", 
                            has response-option $res;
                        $ts isa troubleshooting-session, has identifier {session_id};
                    insert
                        (parent-session: $ts, response: $res, considered-question: $power-ques) isa user-response;
                    """)

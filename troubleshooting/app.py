from inspect import cleandoc

from grakn.client import GraknClient


class Troubleshooter:
    def __init__(self, session_id, keyspace_name="troubleshooting"):

        self._session_id = session_id
        self._user_id = 0  # The migration just adds one user with this ID
        self._keyspace_name = keyspace_name
        self._client = GraknClient(uri="localhost:48555")
        self._session = self._client.session(keyspace=self._keyspace_name)

        # To hold the state between question and response
        self._question_name = None
        self._response_options = []

        with self._session.transaction().write() as tx:
            # Check if the session exists, if not then create it
            if len(list(tx.query(f"match $ts isa troubleshooting-session, "
                                 f"has identifier {self._session_id}; get;"))) == 0:
                tx.query(f"""
                match 
                    $u isa user, has identifier {self._user_id};
                insert 
                    $ts isa troubleshooting-session, has identifier {self._session_id}; 
                    (session-owner: $u, owned-session: $ts) isa session-ownership;
                """)
                tx.commit()

        print("\nWelcome to the Web Conference Troubleshooting App!\n")

    def exit(self):
        self._session.close()
        self._client.close()

    def troubleshoot(self):
        """
        Run a short demo of how a troubleshooting session can work
        Using templates for these queries would be wise, but I want to demonstrate how this works in an easy-to-read way
        :return:
        """
        with self._session.transaction().read() as tx:

            # Find out the product the user is asking about
            # TODO This isn't actually needed in this case since the user has only one product in their account, so it
            #  can be inferred
            # tx.query(f"""
            # match
            #     $u isa user, has identifier {self._user_id};
            #     (owned-product: $p, product-owner: $u) isa product-ownership;
            #     $p isa product, has name $n;
            # get $n;
            # """)

            # Each iteration, query for a fully identified fault (where all of the user's responses match the
            # criteria for this fault
            answers = list(tx.query(f"""
            match
                (diagnosed-fault: $flt, parent-session: $ts) isa diagnosis;
                $ts isa troubleshooting-session, has identifier {self._session_id}; $flt has name $n;
            get $n;
            """))

            if len(answers) > 0:
                # in this case there is a solution, then query for its solution (or part of the same query)
                print(cleandoc(f"""
                A fault has been determined:
                  | {answers[0].get('n').value()}
                """))

            else:
                # Else, query to find the question to ask which will eliminate the most failure scenarios:
                answers = list(tx.query(f"""
                match
                    (diagnosed-fault: $flt, parent-session: $ts) isa candidate-diagnosis;
                    (question-not-asked: $ques, parent-session: $ts) isa unasked-question;
                    ($flt, $ques) isa fault-identification; $ques has name $qu-name;
                get $qu-name, $flt; group $qu-name; count;
                """))
                max_count = 0
                best_question_name = None

                # Sort the answers by question name for consistency in case two have the same importance
                sorted(answers, key=lambda ans: ans.owner().value())

                for answer in answers:
                    count = answer.answers()[0].number()
                    if count >= max_count:
                        max_count = count
                        best_question_name = answer.owner().value()

                # Pick the question with the highest score and ask the user to pick the positive or negative response:
                answers = list(tx.query(f"""
                match 
                    $ques isa question, 
                        has name "{best_question_name}", 
                        has text $text; 
                get $text;
                """))
                print(cleandoc(
                    f"""
                    Question:

                    - | {answers[0].get('text').value()}

                    Pick one answer:

                    """
                ))

                answers = tx.query(f"""
                match 
                    $ques isa question, 
                        has name "{best_question_name}", 
                        has response-option $opt; 
                get $opt;
                """)
                self._question_name = best_question_name
                self._response_options = []

                for i, answer in enumerate(answers):
                    option = answer.get("opt").value()
                    self._response_options.append(option)
                    print(f"{i} | {option}")
                print("")

    def respond(self, response):
        res = None
        try:
            res = self._response_options[response]
        except TypeError:
            if response in self._response_options:
                res = response
            else:
                print("I couldn't understand your response, please either give the number of the answer or type the "
                      "answer out\n")

        if res:
            print(f"Your response was '{response}'\n")
            print("Thanks for your response!\n")
            with self._session.transaction().write() as tx:
                # You can make this more fancy by using some NLP wizardry to interpret their response and map it to one
                # of the available responses

                # insert their response:
                tx.query(f"""
                match
                    $ques isa question, has name "{self._question_name}",
                        has response-option $opt;
                        $opt "{res}";
                    $ts isa troubleshooting-session, has identifier {self._session_id};
                insert
                    (parent-session: $ts, response: $opt, considered-question: $ques) isa user-response;
                """)
                tx.commit()
            self.troubleshoot()

from grakn.client import GraknClient

from templates import fault_template, question_template, failure_mode_template, fault_identification_template, procedure_template, solution_template

FAULT_NAMES = {
    "did not join with audio",
    "muted by host",
    "muted in app",
    "audio permissions not given",
    "low input volume",
    "wrong mic connected",
    "poor connection",
}


QUESTIONS = {
    # question name         question text                            question response options
    "audible to others":    ("Can the participants hear you?",        ("Somewhat",
                                                                       "Not at all")),

    "audio status":         ("What does the button in the bottom "
                             "left of the app window say?",          ("'Mute'",
                                                                      "'Unmute'",
                                                                      "'Join Audio'",
                                                                      "'Mute' with a warning triangle",
                                                                      "'Unmute' with a warning triangle")),

    "voice quality":        ("How do other participants describe "
                             "the problem with your sound?",         ("Faint",
                                                                      "Distorted",
                                                                      "Faint and distorted")),
}

FAILURE_MODES = {
    # product   possible faults
    "standard": FAULT_NAMES,
    "premium":  FAULT_NAMES,
}

FAULT_IDENTIFICATIONS = {
    ("audible to others",   "did not join with audio",      ("Not at all",)),
    ("audible to others",   "muted by host",                ("Not at all",)),
    ("audible to others",   "muted in app",                 ("Not at all",)),
    ("audible to others",   "audio permissions not given",  ("Not at all",)),
    ("audible to others",   "low input volume",             ("Somewhat", "Not at all",)),
    ("audible to others",   "wrong mic connected",          ("Somewhat", "Not at all",)),
    ("audible to others",   "poor connection",              ("Somewhat", "Not at all",)),

    ("audio status",        "did not join with audio",      ("'Join Audio'",)),
    ("audio status",        "muted by host",                ("'Unmute'", "'Unmute' with warning triangle")),
    ("audio status",        "muted in app",                 ("'Unmute'", "'Unmute' with warning triangle")),
    ("audio status",        "audio permissions not given",  ("'Mute' with warning triangle",
                                                             "'Unmute' with warning triangle")),

    ("voice quality",       "low input volume",             ("Faint", "Faint and distorted")),
    ("voice quality",       "wrong mic connected",          ("Faint", "Faint and distorted")),
    ("voice quality",       "poor connection",              ("Distorted", "Faint and distorted")),
}

PROCEDURES = {
    # name                  description
    "Join with audio":      "Click the button in the bottom left that says 'Join Audio', and at the prompt "
                            "select 'Join With Computer Audio'.",

    "Unmute via host":      "If the host has disallowed participants to unmute themselves, then you need to ask the "
                            "host to unmute you via chat.",

    "Unmute mic":           "Click the bottom left button that says 'unmute'. It should then 'mute' when fixed.",

    "Give mic permissions": "Click the button in the bottom left that says 'Join Audio' and there will be a prompt. "
                            "Select 'Go To Settings' then enable access to the microphone for the App.",

    "Increase mic volume":  "Either in the App's settings or system settings, increase the input volume for your "
                            "microphone.",

    "Connect correct mic":  "In the App's settings change the selected microphone to the one you wish to use. Ensure "
                            "that if you are wearing a headset then this is the microphone selected.",

    "Improve connection":   "A slow connection could be caused by other applications making up/downloads. "
                            "Try reducing outgoing network traffic on your connection. Also consider contacting your "
                            "ISP to improve your connection speed.",
}

SOLUTIONS = {
    # fault                             procedure
    ("did not join with audio",         "Join with audio"),
    ("muted by host",                   "Unmute via host"),
    ("muted in app",                    "Unmute mic"),
    ("audio permissions not given",     "Give mic permissions"),
    ("low input volume",                "Increase mic volume"),
    ("wrong mic connected",             "Connect correct mic"),
    ("poor connection",                 "Improve connection"),
}


def migrate(keyspace_name="troubleshooting", schema_path='../schemas/troubleshooting-schema.gql'):
    """
    A migrator to import only a tiny hand-written dataset for demonstration purposes
    """
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace=keyspace_name) as session:

            # First, load the example's schema into grakn directly from the file
            with open(schema_path, 'r') as schema:
                define_query = schema.read()
                with session.transaction().write() as transaction:
                    transaction.query(define_query)
                    transaction.commit()
            print("Loaded the troubleshooting schema")

            # Next, one-by-one load different parts of the data
            with session.transaction().write() as tx:
                tx.query(f"""
                insert 
                
                $u isa user, has identifier 0;
                $acc isa account;
                (group-account: $acc, account-member: $u) isa account-membership;

                $p isa product, has name "standard";
                $p1 isa product, has name "premium";
                
                (owned-product: $p, product-owner: $acc) isa product-ownership; 
                """)
                tx.commit()

            with session.transaction().write() as tx:

                for fault_name in FAULT_NAMES:
                    query = fault_template(fault_name)
                    # print(query)
                    tx.query(query)

                tx.commit()

            with session.transaction().write() as tx:
                for product_name, failure_fault_names in FAILURE_MODES.items():
                    for fault_name in failure_fault_names:
                        query = failure_mode_template(product_name, fault_name)
                        # print(query)
                        tx.query(query)
                tx.commit()

            with session.transaction().write() as tx:

                for question_name, question_fields in QUESTIONS.items():
                    query = question_template(question_name, *question_fields)
                    # print(query)
                    tx.query(query)

                tx.commit()

            with session.transaction().write() as tx:
                for fault_identification in FAULT_IDENTIFICATIONS:
                    query = fault_identification_template(*fault_identification)
                    # print(query)
                    tx.query(query)
                tx.commit()

            with session.transaction().write() as tx:
                for procedure_name, procedure_description in PROCEDURES.items():
                    query = procedure_template(procedure_name, procedure_description)
                    # print(query)
                    tx.query(query)
                tx.commit()

            with session.transaction().write() as tx:
                for solution in SOLUTIONS:
                    query = solution_template(*solution)
                    # print(query)
                    tx.query(query)
                tx.commit()

            print("Migrated the troubleshooting data")


if __name__ == "__main__":
    migrate("troubleshooting")

from grakn.client import GraknClient

from templates import fault_template, question_template

fault_names = [
    "muted by host",
    "mic muted in app",
    "mic muted in system settings",
    "mic faulty",
    "wrong mic connected",
    "mic not connected",
    "audio permissions not given",
    "did not join with audio",
    "internet connection issues",  # jagged or missing audio
    "geographical distance",  # lag
    "mic feedback",  # echo or screeching
]


questions = {
    # question name        question text                            question response options
    "platform":            ("Which platform are you using?",        ("Windows", "OSX", "iOS", "Android")),
    "audible to all":      ("Can all participants hear you?",       ("Yes, all of them", "Some of them",
                                                                     "No, none of them")),
    "audible to any":      ("Can any participant hear you well?",   ("Yes, all of them", "Some of them",
                                                                     "No, none of them")),
    "mute symbol":         ("Does your app show a mute icon?",      ("Yes it does", "No it doesn't")),
    "joined with audio":   ("Did you click yes at the prompt "
                            "'Join with computer audio?'?",       ("Yes I did", "No I didn't")),
}


def migrate(keyspace_name: str):
    """
    A migrator to import only a tiny hand-written dataset for demonstration purposes
    :param keyspace_name:
    :return:
    """
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace=keyspace_name) as session:

            # First, load the example's schema into grakn directly from the file
            with open('schemas/troubleshooting-schema.gql', 'r') as schema:
                define_query = schema.read()
                with session.transaction().write() as transaction:
                    transaction.query(define_query)
                    transaction.commit()
            print("Loaded the troubleshooting schema")

            # Next, one-by-one load different parts of the data
            with session.transaction().write() as tx:

                for fault_name in fault_names:
                    tx.query(fault_template(fault_name))

                tx.commit()

            with session.transaction().write() as tx:

                for question_name, question_fields in questions.items():
                    tx.query(question_template(question_name, *question_fields))

                tx.commit()
            print("Loaded the troubleshooting data")


if __name__ == "__main__":
    migrate("troubleshooting")

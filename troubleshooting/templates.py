from inspect import cleandoc


def fault_template(name: str):
    return cleandoc(f"""
    insert $flt isa fault, has name "{name}";
    """)


def question_template(question_name: str, question_text: str, responses: list):
    query = cleandoc(f"""
    insert
    $ques isa question,
        has name "{question_name}",
        has text "{question_text}";
    """)

    for i, response in enumerate(responses):
        query += cleandoc(f"""\n
        $ques has response-option $r{i};
        $r{i} "{response}";
        """)
    return query


def failure_mode_template(product_name: str, fault_name: str):
    return cleandoc(f"""
    match
    $flt isa fault, has name "{fault_name}";
    $p isa product, has name "{product_name}";
    insert
    (failing-element: $p, failure: $flt) isa failure-mode;
    """)


def fault_identification_template(question_name: str, fault_name: str, question_responses: tuple):
    query = f"""
    match
    $flt isa fault, has name "{fault_name}";
    $ques isa question, has name "{question_name}";
    """
    for i, question_response in enumerate(question_responses):
        query += f"""
        $ques has response-option $res{i};
        $res{i} "{question_response}";
        """

    query += f"""
    insert
    (
    """
    for i, _ in enumerate(question_responses):
        query += f"""
        indicating-response: $res{i},
        """
    query += f"""
    identified-fault: $flt, 
    identifying-question: $ques
    ) isa fault-identification;
    """

    return cleandoc(query)


def procedure_template(procedure_name, procedure_description):
    return cleandoc(f"""
    insert $proc isa procedure, has name "{procedure_name}", has description "{procedure_description}";
    """)


def solution_template(fault_name: str, procedure_name: str):
    return cleandoc(f"""
    match
    $flt isa fault, has name "{fault_name}";
    $proc isa procedure, has name "{procedure_name}";
    insert
    (solving-procedure: $proc, fault-solved: $flt) isa solution;
    """)

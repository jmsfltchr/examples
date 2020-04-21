from inspect import cleandoc


def fault_template(name: str):
    return f'insert $flt isa fault, has name "{name}";'


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


def fault_identification_template(fault_name: str, question_name: str, question_response: str):
    return cleandoc(f"""
    match
    $flt isa fault, has name "{fault_name}";
    $ques isa question, has name "{question_name}";
    $ques has response-option $res;
    $res "{question_response}";
    insert
    (identified-fault: $flt, identifying-question: $ques, indicating-response: $res) isa fault-identification;
    """)


def failure_mode_template(product_name: str, fault_name: str):
    return cleandoc(f"""
    match
    $flt isa fault, has name "{fault_name}";
    $p isa product, has name "{product_name}";
    insert
    (failing-element: $p, failure: $flt) isa failure-mode;
    """)

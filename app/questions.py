"""Question bank and revision notes (offline fallback for Gemini)."""



def _q(qid, topic, level, text, options, answer, course="Python Programming"):
    return {
        "id": qid,
        "course": course,
        "topic": topic,
        "level": level,  # "diag" = diagnostic quiz, "practice" = targeted practice
        "question": text,
        "options": dict(zip("ABCD", options)),
        "answer": answer,
        "source": "bank",
    }


BANK = [
    # Python Basics
    _q("pb1", "Python Basics", "diag", "Which type stores True or False?", ["str", "int", "bool", "float"], "C"),
    _q("pb2", "Python Basics", "diag", "What does type(3.5) return?", ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"], "B"),
    _q("pb3", "Python Basics", "practice", "Which symbol starts a comment in Python?", ["#", "//", "--", "/*"], "A"),
    _q("pb4", "Python Basics", "practice", "What is the result of 7 // 2?", ["3.5", "3", "4", "2"], "B"),
    # Loops
    _q("lp1", "Loops", "diag", "Which loop iterates over a sequence?", ["while", "for", "if", "def"], "B"),
    _q("lp2", "Loops", "diag", "What does list(range(3)) give?", ["[1, 2, 3]", "[0, 1, 2]", "[0, 1, 2, 3]", "[3]"], "B"),
    _q("lp3", "Loops", "practice", "Which statement exits a loop immediately?", ["continue", "pass", "break", "exit"], "C"),
    _q("lp4", "Loops", "practice", "How many times does the body of `for i in range(5)` run?", ["4", "5", "6", "Forever"], "B"),
    # Functions
    _q("fn1", "Functions", "diag", "Which keyword sends a value back from a function?", ["print", "break", "return", "stop"], "C"),
    _q("fn2", "Functions", "diag", "In `def f(x):`, what is x called?", ["loop", "module", "class", "parameter"], "D"),
    _q("fn3", "Functions", "practice", "What does a function return if it has no return statement?", ["0", "None", "False", "An error"], "B"),
    _q("fn4", "Functions", "practice", "Which keyword defines a function?", ["function", "def", "define", "fun"], "B"),
    # Lists & Dicts
    _q("ld1", "Lists & Dicts", "diag", "How do you get the first item of list a?", ["a[1]", "a(0)", "a[0]", "a.first()"], "C"),
    _q("ld2", "Lists & Dicts", "diag", "Which brackets create a dictionary?", ["[]", "()", "{}", "<>"], "C"),
    _q("ld3", "Lists & Dicts", "practice", "Which method adds an item to the end of a list?", ["add", "append", "push", "insert_end"], "B"),
    _q("ld4", "Lists & Dicts", "practice", "How do you read the value of key 'x' in dict d?", ["d.x", "d(x)", "d['x']", "d->x"], "C"),
]

COURSES = sorted({q["course"] for q in BANK})  # add questions with a new course= to add a course

TOPIC_NOTES = {
    "Python Basics": [
        "bool holds True/False; int, float and str are the other core types.",
        "Use type(x) to check a type; // is floor division, / is true division.",
        "Comments start with #.",
    ],
    "Loops": [
        "for x in sequence: repeats once per item; range(n) gives 0..n-1.",
        "while condition: repeats until the condition is False.",
        "break exits the loop, continue skips to the next iteration.",
    ],
    "Functions": [
        "Define with def name(params): and send values back with return.",
        "Parameters are the names in the definition; arguments are the values you pass.",
        "No return statement means the function returns None.",
    ],
    "Lists & Dicts": [
        "Lists are ordered and 0-indexed: a[0] is the first item; a.append(x) adds to the end.",
        "Dicts map keys to values: d['key']; d.get('key') avoids a KeyError.",
        "Lists use [], dicts use {}.",
    ],
}


def public_view(q):
    """Question as sent to the browser: never include the answer key."""
    return {k: v for k, v in q.items() if k not in ("answer", "level")}

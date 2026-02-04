#!/usr/bin/env python3
"""
Python 3 Practice Assessment (IKM-style format, NOT IKM content)

- 54 questions
- Time limit: 135 minutes (configurable)
- Mixed question types:
  * single-choice MCQ (A/B/C/D)
  * multi-select (e.g., A,C)
- Scoring and topic breakdown
"""

from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Dict


# ----------------------------
# Config
# ----------------------------

TOTAL_QUESTIONS = 54
TIME_LIMIT_SECONDS = 135 * 60  # 135 minutes


# ----------------------------
# Data model
# ----------------------------

@dataclass(frozen=True)
class Question:
    prompt: str
    options: List[str]                 # options as strings, index 0 => A, 1 => B ...
    correct: Set[int]                  # set of correct option indexes
    multi_select: bool                 # True => choose one or more
    topic: str                         # for breakdown


# ----------------------------
# Helpers
# ----------------------------

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def idxs_to_letters(idxs: Set[int]) -> str:
    return ",".join(LETTERS[i] for i in sorted(idxs))


def parse_answer(raw: str, multi_select: bool, num_options: int) -> Optional[Set[int]]:
    """
    Accept:
      - Single: "A" or "b"
      - Multi: "A,C" "a c" "AC"
    Returns set of chosen indexes, or None if invalid/blank.
    """
    s = raw.strip().upper()
    if not s:
        return None

    # Normalize separators
    s = s.replace(" ", "").replace(";", ",").replace("/", ",").replace("|", ",")
    if multi_select:
        # allow "AC" as "A,C"
        if "," not in s and len(s) > 1:
            parts = list(s)
        else:
            parts = [p for p in s.split(",") if p]
    else:
        parts = [s[0]]

    chosen: Set[int] = set()
    for p in parts:
        if len(p) != 1 or p not in LETTERS[:num_options]:
            return None
        chosen.add(LETTERS.index(p))

    # For single-select, must pick exactly one
    if not multi_select and len(chosen) != 1:
        return None

    return chosen


def time_left(start: float) -> int:
    elapsed = int(time.time() - start)
    return max(0, TIME_LIMIT_SECONDS - elapsed)


def fmt_mmss(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


# ----------------------------
# Question bank (original practice questions)
# ----------------------------

def build_question_bank() -> List[Question]:
    q: List[Question] = []

    # --- Basics / Syntax ---
    q.append(Question(
        prompt="What is the output of:\n\nprint(type(3/2))",
        options=["<class 'int'>", "<class 'float'>", "<class 'decimal.Decimal'>", "Raises TypeError"],
        correct={1},
        multi_select=False,
        topic="Basics"
    ))
    q.append(Question(
        prompt="Which statement about Python's '==' vs 'is' is TRUE?",
        options=[
            "'is' checks value equality; '==' checks identity",
            "'==' checks value equality; 'is' checks identity",
            "'is' and '==' are interchangeable for integers",
            "'==' is only for strings"
        ],
        correct={1},
        multi_select=False,
        topic="Basics"
    ))
    q.append(Question(
        prompt="What does this print?\n\nx = [1, 2, 3]\ny = x\nx.append(4)\nprint(y)",
        options=["[1, 2, 3]", "[1, 2, 3, 4]", "[4]", "Raises NameError"],
        correct={1},
        multi_select=False,
        topic="References"
    ))
    q.append(Question(
        prompt="What is the result of:\n\n(1, 2, 3)[1:]",
        options=["(1,)", "(2, 3)", "[2, 3]", "Raises TypeError"],
        correct={1},
        multi_select=False,
        topic="Sequences"
    ))
    q.append(Question(
        prompt="Which of the following are valid dictionary keys? (Select ALL that apply)",
        options=["('a', 1)", "['a', 1]", "{'a': 1}", "42"],
        correct={0, 3},
        multi_select=True,
        topic="Data Structures"
    ))

    # --- Functions / Scope ---
    q.append(Question(
        prompt="What does this print?\n\ndef f(x, acc=[]):\n    acc.append(x)\n    return acc\n\nprint(f(1))\nprint(f(2))",
        options=["[1] then [2]", "[1] then [1, 2]", "[1] then [1]", "Raises TypeError"],
        correct={1},
        multi_select=False,
        topic="Functions"
    ))
    q.append(Question(
        prompt="Given:\n\nx = 10\n\ndef g():\n    x = 5\n\ng()\nprint(x)\n\nWhat is printed?",
        options=["5", "10", "UnboundLocalError", "NameError"],
        correct={1},
        multi_select=False,
        topic="Scope"
    ))
    q.append(Question(
        prompt="Which keyword declares that a variable lives in an enclosing (non-global) scope?",
        options=["global", "static", "nonlocal", "outer"],
        correct={2},
        multi_select=False,
        topic="Scope"
    ))
    q.append(Question(
        prompt="Which of the following create a generator? (Select ALL that apply)",
        options=[
            "(x*x for x in range(3))",
            "[x*x for x in range(3)]",
            "def h():\n    yield 1",
            "{x*x for x in range(3)}"
        ],
        correct={0, 2},
        multi_select=True,
        topic="Iterators/Generators"
    ))

    # --- Exceptions ---
    q.append(Question(
        prompt="What is the purpose of the 'else' block on a try statement?",
        options=[
            "Runs if an exception occurs",
            "Runs only if no exception occurs",
            "Runs regardless of exceptions",
            "Runs only if a finally block exists"
        ],
        correct={1},
        multi_select=False,
        topic="Exceptions"
    ))
    q.append(Question(
        prompt="What happens here?\n\ntry:\n    1/0\nfinally:\n    print('done')",
        options=["Prints 'done' then exits normally", "Prints 'done' then raises ZeroDivisionError", "Raises before printing", "SyntaxError"],
        correct={1},
        multi_select=False,
        topic="Exceptions"
    ))

    # --- Collections / Algorithms ---
    q.append(Question(
        prompt="What is the output?\n\nprint(sorted(['10','2','1']))",
        options=["['1', '2', '10']", "['10', '1', '2']", "['10', '2', '1']", "TypeError"],
        correct={1},
        multi_select=False,
        topic="Sorting"
    ))
    q.append(Question(
        prompt="Which is the time complexity of average-case dictionary lookup by key?",
        options=["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        correct={0},
        multi_select=False,
        topic="Complexity"
    ))
    q.append(Question(
        prompt="What does this produce?\n\n{n: n*n for n in range(3)}",
        options=["{0, 1, 4}", "{0: 0, 1: 1, 2: 4}", "[(0,0),(1,1),(2,4)]", "Raises SyntaxError"],
        correct={1},
        multi_select=False,
        topic="Comprehensions"
    ))

    # --- Strings / Bytes ---
    q.append(Question(
        prompt="What is the type of b'abc'?",
        options=["str", "bytes", "bytearray", "memoryview"],
        correct={1},
        multi_select=False,
        topic="Strings/Bytes"
    ))
    q.append(Question(
        prompt="Which of the following are TRUE about Python strings? (Select ALL that apply)",
        options=[
            "Strings are mutable",
            "Strings are sequences",
            "Strings support slicing",
            "Strings are interned in all cases"
        ],
        correct={1, 2},
        multi_select=True,
        topic="Strings/Bytes"
    ))

    # --- OOP ---
    q.append(Question(
        prompt="What does @staticmethod do?",
        options=[
            "Passes instance as first argument",
            "Passes class as first argument",
            "Creates a function stored on the class without implicit first argument",
            "Makes method private"
        ],
        correct={2},
        multi_select=False,
        topic="OOP"
    ))
    q.append(Question(
        prompt="What does this print?\n\nclass A:\n    def f(self):\n        return 'A'\n\nclass B(A):\n    def f(self):\n        return super().f() + 'B'\n\nprint(B().f())",
        options=["A", "B", "AB", "BA"],
        correct={2},
        multi_select=False,
        topic="OOP"
    ))

    # --- Standard library / IO ---
    q.append(Question(
        prompt="Which module is commonly used to serialize Python objects to JSON?",
        options=["pickle", "json", "marshal", "csv"],
        correct={1},
        multi_select=False,
        topic="Stdlib"
    ))
    q.append(Question(
        prompt="Which statement about 'with open(...) as f:' is TRUE?",
        options=[
            "It prevents buffering",
            "It automatically closes the file even if exceptions occur",
            "It makes file reads faster by default",
            "It disables exceptions"
        ],
        correct={1},
        multi_select=False,
        topic="IO"
    ))

    # --- Concurrency ---
    q.append(Question(
        prompt="In CPython, the GIL primarily affects which scenario?",
        options=[
            "I/O-bound threads cannot run concurrently",
            "CPU-bound Python bytecode in threads does not execute in true parallel",
            "Multiprocessing cannot use multiple cores",
            "Asyncio tasks are blocked by the GIL"
        ],
        correct={1},
        multi_select=False,
        topic="Concurrency"
    ))

    # --- Typing / Dataclasses ---
    q.append(Question(
        prompt="What does typing.Optional[int] mean?",
        options=["int only", "int or None", "Any type", "A required integer"],
        correct={1},
        multi_select=False,
        topic="Typing"
    ))

    # --- Add more to reach a robust pool ---
    # We'll programmatically add a bunch of additional original questions to ensure we can sample 54.

    extra: List[Question] = [
        Question(
            prompt="What is printed?\n\nprint(list(range(5))[::2])",
            options=["[0, 1, 2]", "[0, 2, 4]", "[1, 3, 5]", "TypeError"],
            correct={1}, multi_select=False, topic="Sequences"
        ),
        Question(
            prompt="What is the output?\n\nx = (1)\nprint(type(x))",
            options=["<class 'tuple'>", "<class 'int'>", "<class 'list'>", "<class 'float'>"],
            correct={1}, multi_select=False, topic="Basics"
        ),
        Question(
            prompt="What is the output?\n\nx = (1,)\nprint(type(x))",
            options=["<class 'tuple'>", "<class 'int'>", "<class 'list'>", "<class 'float'>"],
            correct={0}, multi_select=False, topic="Basics"
        ),
        Question(
            prompt="Which are valid ways to copy a list 'a'? (Select ALL that apply)",
            options=["a.copy()", "list(a)", "a[:]", "copy(a)"],
            correct={0,1,2}, multi_select=True, topic="Data Structures"
        ),
        Question(
            prompt="What does this print?\n\nprint(bool([]), bool([0]))",
            options=["False False", "True False", "False True", "True True"],
            correct={2}, multi_select=False, topic="Truthiness"
        ),
        Question(
            prompt="Which exception is raised when you access a missing dict key using d[key]?",
            options=["IndexError", "KeyError", "ValueError", "AttributeError"],
            correct={1}, multi_select=False, topic="Exceptions"
        ),
        Question(
            prompt="Which method adds an element to a set?",
            options=["append", "add", "push", "insert"],
            correct={1}, multi_select=False, topic="Data Structures"
        ),
        Question(
            prompt="What will this do?\n\ndef f():\n    return\n\nprint(f())",
            options=["prints nothing", "prints False", "prints None", "raises SyntaxError"],
            correct={2}, multi_select=False, topic="Functions"
        ),
        Question(
            prompt="Which are TRUE about list comprehensions? (Select ALL that apply)",
            options=[
                "They can include an if filter",
                "They always create generators",
                "They can be nested",
                "They mutate the original list automatically"
            ],
            correct={0,2}, multi_select=True, topic="Comprehensions"
        ),
        Question(
            prompt="What does this print?\n\nprint('a' * 3)",
            options=["aaa", "a3", "Error", "['a','a','a']"],
            correct={0}, multi_select=False, topic="Strings/Bytes"
        ),
        Question(
            prompt="Which built-in converts an iterable of pairs into a dict?",
            options=["map", "dict", "tuple", "set"],
            correct={1}, multi_select=False, topic="Stdlib"
        ),
        Question(
            prompt="What does enumerate(iterable) yield?",
            options=[
                "Only indexes",
                "Only items",
                "Pairs of (index, item)",
                "Triples of (index, item, length)"
            ],
            correct={2}, multi_select=False, topic="Iterators/Generators"
        ),
        Question(
            prompt="Which statement about Python's default argument evaluation is correct?",
            options=[
                "Evaluated at call time",
                "Evaluated at function definition time",
                "Evaluated when imported only",
                "Evaluated per module reload only"
            ],
            correct={1}, multi_select=False, topic="Functions"
        ),
        Question(
            prompt="What is the output?\n\nprint({1,2,2,3})",
            options=["{1, 2, 2, 3}", "{1, 2, 3}", "[1,2,3]", "Error"],
            correct={1}, multi_select=False, topic="Data Structures"
        ),
        Question(
            prompt="Which are TRUE about tuples? (Select ALL that apply)",
            options=[
                "Tuples are immutable",
                "Tuples can contain mutable objects",
                "Tuples can be dictionary keys if all items are hashable",
                "Tuples are always sorted"
            ],
            correct={0,1,2}, multi_select=True, topic="Data Structures"
        ),
        Question(
            prompt="What does this print?\n\nprint(len({'a':1, 'b':2}))",
            options=["1", "2", "3", "Error"],
            correct={1}, multi_select=False, topic="Data Structures"
        ),
        Question(
            prompt="Which of these are valid exception base classes? (Select ALL that apply)",
            options=["BaseException", "Exception", "Error", "Throwable"],
            correct={0,1}, multi_select=True, topic="Exceptions"
        ),
        Question(
            prompt="Which statement about 'finally' is TRUE?",
            options=[
                "It runs only if no exception occurs",
                "It runs only if an exception occurs",
                "It runs regardless, except in some abrupt termination cases",
                "It is the same as else"
            ],
            correct={2}, multi_select=False, topic="Exceptions"
        ),
        Question(
            prompt="What is printed?\n\nprint(','.join(['a','b','c']))",
            options=["a b c", "a,b,c", "['a','b','c']", "Error"],
            correct={1}, multi_select=False, topic="Strings/Bytes"
        ),
        Question(
            prompt="Which are TRUE about pathlib.Path? (Select ALL that apply)",
            options=[
                "It provides an object-oriented filesystem path API",
                "It replaces the need for os.path in many cases",
                "It can open files via Path.open()",
                "It can only represent absolute paths"
            ],
            correct={0,1,2}, multi_select=True, topic="IO"
        ),
        Question(
            prompt="What is the output?\n\nprint(sum([1,2,3], 10))",
            options=["6", "16", "TypeError", "13"],
            correct={1}, multi_select=False, topic="Stdlib"
        ),
        Question(
            prompt="Which are TRUE about f-strings? (Select ALL that apply)",
            options=[
                "They are evaluated at runtime",
                "They can include expressions inside braces",
                "They require Python 2",
                "They always escape braces automatically without doubling"
            ],
            correct={0,1}, multi_select=True, topic="Strings/Bytes"
        ),
        Question(
            prompt="What is the output?\n\nx = [1,2,3]\nprint(x.pop())\nprint(x)",
            options=["prints 1 then [2,3]", "prints 3 then [1,2]", "prints 3 then [1,2,3]", "Error"],
            correct={1}, multi_select=False, topic="Data Structures"
        ),
        Question(
            prompt="Which statement about 'async def' is TRUE?",
            options=[
                "It defines a generator function by default",
                "It defines a coroutine function",
                "It starts running immediately when defined",
                "It can only be used inside classes"
            ],
            correct={1}, multi_select=False, topic="Concurrency"
        ),
    ]

    q.extend(extra)

    # Ensure a large enough bank by cloning structure with different prompts/options
    # (All original; no IKM content.)
    generated: List[Question] = []
    for i in range(1, 61):
        generated.append(Question(
            prompt=f"Consider:\n\nitems = list(range({i%10 + 5}))\n\nWhich expression returns the last element?",
            options=["items[-1]", "items[last]", "items[len(items)]", "items.get(-1)"],
            correct={0},
            multi_select=False,
            topic="Sequences"
        ))
    q.extend(generated)

    # Another batch of original questions
    for i in range(1, 61):
        n = i % 7 + 2
        q.append(Question(
            prompt=f"What is the result of:\n\nlen(set([1]*{n} + [2]*{n}))",
            options=[str(1), str(2), str(n), "Raises TypeError"],
            correct={1},
            multi_select=False,
            topic="Data Structures"
        ))

    return q


# ----------------------------
# Exam engine
# ----------------------------

def run_exam(questions: List[Question]) -> None:
    random.shuffle(questions)
    exam = questions[:TOTAL_QUESTIONS]

    start = time.time()
    per_topic: Dict[str, Tuple[int, int]] = {}  # topic -> (correct, total)

    correct_count = 0

    print("\nPython 3 Practice Assessment")
    print(f"Questions: {TOTAL_QUESTIONS}")
    print(f"Time limit: {TIME_LIMIT_SECONDS // 60} minutes")
    print("Answer format: A / B / C / D (or A,C for multi-select).")
    print("Type 'q' to quit.\n")

    for i, q in enumerate(exam, start=1):
        remaining = time_left(start)
        if remaining <= 0:
            print("\nTime is up!")
            break

        print("=" * 70)
        print(f"Q{i}/{TOTAL_QUESTIONS}  |  Topic: {q.topic}  |  Time left: {fmt_mmss(remaining)}\n")
        print(q.prompt)
        print()

        for idx, opt in enumerate(q.options):
            print(f"  {LETTERS[idx]}. {opt}")

        if q.multi_select:
            print("\n(Select ALL that apply. Example: A,C)")
        else:
            print("\n(Select ONE answer.)")

        # Input loop
        while True:
            remaining = time_left(start)
            if remaining <= 0:
                print("\nTime is up!")
                break

            raw = input("Your answer: ").strip()
            if raw.lower() == "q":
                print("\nExiting exam early.")
                show_results(correct_count, i - 1, per_topic)
                return

            chosen = parse_answer(raw, q.multi_select, len(q.options))
            if chosen is None:
                print("Invalid input. Try again (e.g., A or A,C).")
                continue

            is_correct = chosen == q.correct
            # topic totals
            c, t = per_topic.get(q.topic, (0, 0))
            per_topic[q.topic] = (c + (1 if is_correct else 0), t + 1)

            if is_correct:
                print("Correct!\n")
                correct_count += 1
            else:
                print(f"Incorrect. Correct answer: {idxs_to_letters(q.correct)}\n")
            break

        if time_left(start) <= 0:
            break

    attempted = sum(t for _, t in per_topic.values())
    show_results(correct_count, attempted, per_topic)


def show_results(correct: int, attempted: int, per_topic: Dict[str, Tuple[int, int]]) -> None:
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    if attempted == 0:
        print("No questions attempted.")
        return

    score_pct = (correct / attempted) * 100.0
    print(f"Attempted: {attempted}")
    print(f"Correct:   {correct}")
    print(f"Score:     {score_pct:.1f}%")

    print("\nTopic breakdown:")
    # Sort by most questions attempted, then worst performing
    rows = []
    for topic, (c, t) in per_topic.items():
        pct = (c / t) * 100.0 if t else 0.0
        rows.append((t, pct, topic, c))
    rows.sort(key=lambda x: (-x[0], x[1]))

    for t, pct, topic, c in rows:
        print(f"  {topic:18s}  {c:2d}/{t:2d}  ({pct:5.1f}%)")

    print("\nTip: Re-run to get a different question mix.\n")


def main() -> int:
    bank = build_question_bank()
    if len(bank) < TOTAL_QUESTIONS:
        print("Question bank too small.")
        return 1

    run_exam(bank)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

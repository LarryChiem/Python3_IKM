#!/usr/bin/env python3
"""
Python 3 Practice Assessment (original content; not IKM questions)

Features:
- 54 questions per run (sampled from a 110+ question bank)
- 135-minute time limit
- Single-choice + multi-select
- Topic breakdown
- Review missed questions at end (optional)
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional


TOTAL_QUESTIONS = 54
TIME_LIMIT_SECONDS = 135 * 60  # 135 minutes
REVIEW_MISSED_AT_END = True

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass(frozen=True)
class Question:
    prompt: str
    options: List[str]          # A, B, C, ...
    correct: Set[int]           # indexes
    multi_select: bool
    topic: str
    explanation: str = ""       # short, for learning


def idxs_to_letters(idxs: Set[int]) -> str:
    return ",".join(LETTERS[i] for i in sorted(idxs))


def parse_answer(raw: str, multi_select: bool, num_options: int) -> Optional[Set[int]]:
    s = raw.strip().upper()
    if not s:
        return None
    if s.lower() == "q":
        return set([-1])  # sentinel

    # Normalize separators; allow "AC" for multi-select
    s = s.replace(" ", "").replace(";", ",").replace("/", ",").replace("|", ",")
    if multi_select:
        if "," not in s and len(s) > 1:
            parts = list(s)
        else:
            parts = [p for p in s.split(",") if p]
    else:
        parts = [s[0]]

    chosen: Set[int] = set()
    for p in parts:
        if len(p) != 1:
            return None
        if p not in LETTERS[:num_options]:
            return None
        chosen.add(LETTERS.index(p))

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


def q(prompt: str, options: List[str], correct_letters: str, topic: str, explanation: str = "") -> Question:
    correct_set = set()
    for ch in correct_letters.replace(" ", "").split(","):
        ch = ch.strip().upper()
        if not ch:
            continue
        correct_set.add(LETTERS.index(ch))
    multi = len(correct_set) > 1
    return Question(prompt=prompt, options=options, correct=correct_set, multi_select=multi, topic=topic, explanation=explanation)


def build_bank() -> List[Question]:
    B: List[Question] = []

    # ---------------- Basics & Operators ----------------
    B.append(q(
        "What is the output?\n\nprint(type(3/2))",
        ["<class 'int'>", "<class 'float'>", "<class 'decimal.Decimal'>", "TypeError"],
        "B", "Basics",
        "In Python 3, / always produces float."
    ))
    B.append(q(
        "Which statement is TRUE about '==' and 'is'?",
        ["'is' checks value equality; '==' checks identity",
         "'==' checks value equality; 'is' checks identity",
         "'is' and '==' are always interchangeable",
         "'is' is for strings only"],
        "B", "Basics",
        "'is' compares object identity; '==' compares value equality."
    ))
    B.append(q(
        "What does this print?\n\nprint(0.1 + 0.2 == 0.3)",
        ["True", "False", "Raises ValueError", "Depends on OS"],
        "B", "Numerics",
        "Floating-point rounding makes 0.1+0.2 not exactly 0.3."
    ))
    B.append(q(
        "What does this print?\n\nprint(5 // 2, -5 // 2)",
        ["2 -2", "2 -3", "2 3", "2 -1"],
        "B", "Numerics",
        "Floor division rounds down (toward -infinity)."
    ))
    B.append(q(
        "Which are valid dictionary keys? (Select ALL that apply)",
        ["('a', 1)", "['a', 1]", "{'a': 1}", "42"],
        "A,D", "Data Structures",
        "Keys must be hashable/immutable; tuples (if hashable) and ints are fine."
    ))

    # ---------------- Strings / Bytes ----------------
    B.append(q(
        "What is the output?\n\nprint('a' * 3)",
        ["aaa", "a3", "Error", "['a','a','a']"],
        "A", "Strings"
    ))
    B.append(q(
        "What is printed?\n\nprint(','.join(['a', 'b', 'c']))",
        ["a b c", "a,b,c", "['a','b','c']", "TypeError"],
        "B", "Strings"
    ))
    B.append(q(
        "Which are TRUE about Python strings? (Select ALL that apply)",
        ["Strings are mutable", "Strings are sequences", "Strings support slicing", "Strings are always interned"],
        "B,C", "Strings",
        "Strings are immutable sequences; interning is an optimization not guaranteed."
    ))
    B.append(q(
        "What is the type of b'abc'?",
        ["str", "bytes", "bytearray", "memoryview"],
        "B", "Strings"
    ))
    B.append(q(
        "What does this print?\n\nprint('hello'[:3])",
        ["hel", "ell", "llo", "IndexError"],
        "A", "Strings"
    ))
    B.append(q(
        "Which expression converts bytes to str assuming UTF-8?",
        ["bytes('x')", "b.decode('utf-8')", "str(b, 'bytes')", "b.encode('utf-8')"],
        "B", "Strings",
        "decode converts bytes -> str; encode converts str -> bytes."
    ))

    # ---------------- Lists / Tuples / Sets ----------------
    B.append(q(
        "What is the output?\n\nx = (1)\nprint(type(x))",
        ["<class 'tuple'>", "<class 'int'>", "<class 'list'>", "<class 'float'>"],
        "B", "Sequences",
        "(1) is just 1; a 1-tuple is (1,)."
    ))
    B.append(q(
        "What is the output?\n\nx = (1,)\nprint(type(x))",
        ["<class 'tuple'>", "<class 'int'>", "<class 'list'>", "<class 'float'>"],
        "A", "Sequences"
    ))
    B.append(q(
        "What does this print?\n\nx = [1,2,3]\ny = x\nx.append(4)\nprint(y)",
        ["[1,2,3]", "[1,2,3,4]", "[4]", "NameError"],
        "B", "References",
        "y references the same list as x."
    ))
    B.append(q(
        "What does this print?\n\nx = [1,2,3]\ny = x[:] \nx.append(4)\nprint(y)",
        ["[1,2,3,4]", "[1,2,3]", "[]", "TypeError"],
        "B", "References",
        "Slicing makes a shallow copy of the list."
    ))
    B.append(q(
        "Which are valid ways to copy list a? (Select ALL that apply)",
        ["a.copy()", "list(a)", "a[:]", "copy(a)"],
        "A,B,C", "Data Structures",
        "copy(a) isn't a builtin; you'd need copy.copy from the copy module."
    ))
    B.append(q(
        "What is printed?\n\nprint({1,2,2,3})",
        ["{1, 2, 2, 3}", "{1, 2, 3}", "[1,2,3]", "Error"],
        "B", "Data Structures",
        "Sets remove duplicates."
    ))
    B.append(q(
        "What does this print?\n\nx = [1,2,3]\nprint(x.pop())\nprint(x)",
        ["1 then [2,3]", "3 then [1,2]", "3 then [1,2,3]", "TypeError"],
        "B", "Data Structures"
    ))
    B.append(q(
        "Which method adds an element to a set?",
        ["append", "add", "push", "insert"],
        "B", "Data Structures"
    ))
    B.append(q(
        "Which are TRUE about tuples? (Select ALL that apply)",
        ["Tuples are immutable", "Tuples can contain mutable objects", "Tuples can be dict keys if all items are hashable", "Tuples are always sorted"],
        "A,B,C", "Data Structures"
    ))

    # ---------------- Dicts / Comprehensions ----------------
    B.append(q(
        "What is the result of:\n\n{n: n*n for n in range(3)}",
        ["{0,1,4}", "{0:0, 1:1, 2:4}", "[(0,0),(1,1),(2,4)]", "SyntaxError"],
        "B", "Comprehensions"
    ))
    B.append(q(
        "What does dict.get(key, default) do when key is missing?",
        ["Raises KeyError", "Returns None always", "Returns default (or None if not provided)", "Adds key with default"],
        "C", "Data Structures"
    ))
    B.append(q(
        "What is printed?\n\nd = {'a': 1}\nprint(d.setdefault('b', 2), d)",
        ["2 {'a':1, 'b':2}", "None {'a':1}", "KeyError", "2 {'a':1}"],
        "A", "Data Structures",
        "setdefault inserts the key with default if missing, and returns the value."
    ))
    B.append(q(
        "Which comprehension creates a set?",
        ["(x for x in range(3))", "[x for x in range(3)]", "{x for x in range(3)}", "{x: x for x in range(3)}"],
        "C", "Comprehensions"
    ))
    B.append(q(
        "What does this print?\n\nprint({}.fromkeys(['a','b'], []))",
        ["{'a': [], 'b': []} with independent lists", "SyntaxError", "TypeError", "Both keys share the same list object"],
        "D", "Pitfalls",
        "fromkeys uses the same value object for all keys unless you create per-key values."
    ))

    # ---------------- Truthiness ----------------
    B.append(q(
        "What does this print?\n\nprint(bool([]), bool([0]))",
        ["False False", "True False", "False True", "True True"],
        "C", "Truthiness"
    ))
    B.append(q(
        "Which values are falsy in Python? (Select ALL that apply)",
        ["0", "''", "[]", "'0'"],
        "A,B,C", "Truthiness"
    ))

    # ---------------- Functions / Args ----------------
    B.append(q(
        "What does this print?\n\ndef f(x, acc=[]):\n    acc.append(x)\n    return acc\n\nprint(f(1))\nprint(f(2))",
        ["[1] then [2]", "[1] then [1, 2]", "[1] then [1]", "TypeError"],
        "B", "Functions",
        "Default args are evaluated once at definition time."
    ))
    B.append(q(
        "Which call passes 3 as 'c'?\n\ndef f(a, b=2, *, c=3):\n    return a+b+c",
        ["f(1, 2, 3)", "f(1, c=3)", "f(1, 2, c=3)", "f(a=1, 2, c=3)"],
        "B,C", "Functions",
        "c is keyword-only due to '*'."
    ))
    B.append(q(
        "What does this print?\n\ndef g(*args, **kwargs):\n    return args, kwargs\n\nprint(g(1,2,x=3))",
        ["((1,2), {'x':3})", "([1,2], {'x':3})", "(1,2,{'x':3})", "TypeError"],
        "A", "Functions"
    ))
    B.append(q(
        "What does this print?\n\ndef f():\n    return\n\nprint(f())",
        ["prints nothing", "prints False", "prints None", "SyntaxError"],
        "C", "Functions"
    ))

    # ---------------- Scope / Closures ----------------
    B.append(q(
        "What is printed?\n\nx = 10\n\ndef g():\n    x = 5\n\ng()\nprint(x)",
        ["5", "10", "UnboundLocalError", "NameError"],
        "B", "Scope"
    ))
    B.append(q(
        "Which keyword assigns to a variable in an enclosing (non-global) scope?",
        ["global", "static", "nonlocal", "outer"],
        "C", "Scope"
    ))
    B.append(q(
        "What happens?\n\nx = 1\n\ndef h():\n    print(x)\n    x = 2\n\nh()",
        ["Prints 1", "Prints 2", "UnboundLocalError", "NameError"],
        "C", "Scope",
        "Assignment makes x local; read before assignment triggers UnboundLocalError."
    ))

    # ---------------- Iterators / Generators ----------------
    B.append(q(
        "Which create a generator? (Select ALL that apply)",
        ["(x*x for x in range(3))", "[x*x for x in range(3)]", "def h():\n    yield 1", "{x*x for x in range(3)}"],
        "A,C", "Iterators/Generators"
    ))
    B.append(q(
        "What is printed?\n\nit = iter([1,2])\nprint(next(it))\nprint(next(it))",
        ["1 then 2", "2 then 1", "1 then 1", "StopIteration immediately"],
        "A", "Iterators/Generators"
    ))
    B.append(q(
        "What happens on the third next()?\n\nit = iter([1,2])\nnext(it)\nnext(it)\nnext(it)",
        ["Returns None", "Raises StopIteration", "Loops back to start", "TypeError"],
        "B", "Iterators/Generators"
    ))

    # ---------------- Sorting ----------------
    B.append(q(
        "What is the output?\n\nprint(sorted(['10','2','1']))",
        ["['1','2','10']", "['10','1','2']", "['10','2','1']", "TypeError"],
        "B", "Sorting",
        "Strings sort lexicographically."
    ))
    B.append(q(
        "Which sorted call sorts numbers by absolute value?",
        ["sorted(nums, key=abs)", "sorted(abs(nums))", "sorted(nums).abs()", "sort(nums, abs)"],
        "A", "Sorting"
    ))
    B.append(q(
        "In list.sort(), what does 'reverse=True' do?",
        ["Sorts by reverse key", "Sorts descending", "Randomizes ties", "Sorts by type"],
        "B", "Sorting"
    ))

    # ---------------- Exceptions ----------------
    B.append(q(
        "Purpose of try/else?",
        ["Runs if exception occurs", "Runs only if no exception occurs", "Runs regardless", "Runs only with finally"],
        "B", "Exceptions"
    ))
    B.append(q(
        "What happens here?\n\ntry:\n    1/0\nfinally:\n    print('done')",
        ["Prints done then continues normally", "Prints done then raises ZeroDivisionError", "Raises before printing", "SyntaxError"],
        "B", "Exceptions"
    ))
    B.append(q(
        "Which exception is raised for missing dict key using d[key]?",
        ["IndexError", "KeyError", "ValueError", "AttributeError"],
        "B", "Exceptions"
    ))
    B.append(q(
        "Which are valid exception base classes? (Select ALL that apply)",
        ["BaseException", "Exception", "Error", "Throwable"],
        "A,B", "Exceptions"
    ))
    B.append(q(
        "What does 'raise' with no args do inside an except block?",
        ["Raises SyntaxError", "Re-raises the current exception", "Raises None", "Clears the exception"],
        "B", "Exceptions"
    ))

    # ---------------- Files / Context managers ----------------
    B.append(q(
        "Which is TRUE about 'with open(...) as f:'?",
        ["Prevents buffering", "Automatically closes file even if exceptions occur", "Makes reads faster", "Disables exceptions"],
        "B", "IO"
    ))
    B.append(q(
        "Which mode opens a file for appending text?",
        ["'r'", "'w'", "'a'", "'rb'"],
        "C", "IO"
    ))
    B.append(q(
        "What does this print?\n\nfrom pathlib import Path\np = Path('a') / 'b'\nprint(str(p).endswith('a' + str(Path.sep) + 'b'))",
        ["True", "False", "Depends on OS", "Raises AttributeError"],
        "C", "IO",
        "Path separator is OS-dependent; you shouldn't rely on string concatenation like that."
    ))
    B.append(q(
        "Which are TRUE about pathlib.Path? (Select ALL that apply)",
        ["Object-oriented path API", "Replaces os.path in many cases", "Can open via Path.open()", "Only represents absolute paths"],
        "A,B,C", "IO"
    ))

    # ---------------- Stdlib ----------------
    B.append(q(
        "Which module is commonly used to serialize data to JSON?",
        ["pickle", "json", "marshal", "csv"],
        "B", "Stdlib"
    ))
    B.append(q(
        "What is the output?\n\nprint(sum([1,2,3], 10))",
        ["6", "16", "TypeError", "13"],
        "B", "Stdlib",
        "sum(iterable, start) starts from 10."
    ))
    B.append(q(
        "Which tool is best for counting hashable items in an iterable?",
        ["collections.Counter", "itertools.count", "functools.reduce", "statistics.mean"],
        "A", "Stdlib"
    ))
    B.append(q(
        "Which function turns an iterable of pairs into a dict?",
        ["map", "dict", "tuple", "set"],
        "B", "Stdlib"
    ))
    B.append(q(
        "What does enumerate(iterable) yield?",
        ["Only indexes", "Only items", "Pairs of (index, item)", "Triples (index, item, length)"],
        "C", "Stdlib"
    ))

    # ---------------- OOP ----------------
    B.append(q(
        "What does @staticmethod do?",
        ["Passes instance as first arg", "Passes class as first arg", "No implicit first argument", "Makes method private"],
        "C", "OOP"
    ))
    B.append(q(
        "What does @classmethod receive as its first argument?",
        ["self", "cls", "Both self and cls", "Nothing"],
        "B", "OOP"
    ))
    B.append(q(
        "What prints?\n\nclass A:\n    def f(self):\n        return 'A'\n\nclass B(A):\n    def f(self):\n        return super().f() + 'B'\n\nprint(B().f())",
        ["A", "B", "AB", "BA"],
        "C", "OOP"
    ))
    B.append(q(
        "If a class defines __len__ returning 0, what is bool(obj)?",
        ["True", "False", "TypeError", "Depends on __bool__ only"],
        "B", "OOP",
        "If __bool__ not defined, Python uses __len__ for truthiness."
    ))
    B.append(q(
        "Which special method is used for 'obj[index]'?",
        ["__getitem__", "__getattr__", "__index__", "__slice__"],
        "A", "OOP"
    ))

    # ---------------- Concurrency (basics) ----------------
    B.append(q(
        "In CPython, the GIL primarily means:",
        ["I/O-bound threads can't overlap", "CPU-bound Python bytecode in threads doesn't run in true parallel", "multiprocessing can't use multiple cores", "asyncio is blocked by the GIL"],
        "B", "Concurrency"
    ))
    B.append(q(
        "Which is typically best for many concurrent network requests in Python?",
        ["threading for CPU math", "asyncio for lots of I/O tasks", "multiprocessing for single-core", "recursion for I/O"],
        "B", "Concurrency"
    ))
    B.append(q(
        "What does 'await' require on its right-hand side?",
        ["A normal function", "An awaitable (e.g., coroutine/future/task)", "A generator only", "A thread"],
        "B", "Concurrency"
    ))

    # ---------------- Typing / Dataclasses ----------------
    B.append(q(
        "typing.Optional[int] means:",
        ["int only", "int or None", "Any type", "Required int"],
        "B", "Typing"
    ))
    B.append(q(
        "What does a dataclass primarily generate?",
        ["Only __init__", "Only __repr__", "Boilerplate methods like __init__/__repr__/__eq__", "A metaclass"],
        "C", "Typing"
    ))

    # ---------------- Pitfalls / Semantics ----------------
    B.append(q(
        "What does this print?\n\nprint([[]] * 3)",
        ["[[], [], []] three independent lists", "[[]] repeated references to the same inner list", "TypeError", "[]"],
        "B", "Pitfalls",
        "List multiplication repeats references to the same inner object."
    ))
    B.append(q(
        "Given:\n\nx = [[]] * 2\nx[0].append(1)\nprint(x)\n\nWhat prints?",
        ["[[1], []]", "[[1], [1]]", "[[], []]", "TypeError"],
        "B", "Pitfalls"
    ))
    B.append(q(
        "What is the output?\n\nprint({}.fromkeys([1,2,3], 0))",
        ["{1:0,2:0,3:0}", "{0:1,0:2,0:3}", "TypeError", "Random order values"],
        "A", "Pitfalls"
    ))
    B.append(q(
        "Which statement about Python evaluation order is TRUE?",
        ["Function arguments are evaluated left-to-right", "Right-to-left", "Random", "Depends on interpreter flags"],
        "A", "Semantics"
    ))
    B.append(q(
        "What does this print?\n\nprint('x' in {'x': 1})",
        ["True", "False", "TypeError", "Depends on hash seed"],
        "A", "Data Structures",
        "'in' checks keys for dict membership."
    ))

    # ---------------- Complexity ----------------
    B.append(q(
        "Average-case time complexity of dict lookup by key?",
        ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "A", "Complexity"
    ))
    B.append(q(
        "Average-case time complexity of checking membership in a set?",
        ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
        "A", "Complexity"
    ))

    # ---------------- More varied “code reading” questions ----------------
    B.append(q(
        "What is printed?\n\ndef f(n):\n    return , funcs, funcs)",
        ["10 11 12", "12 12 12", "13 13 13", "11 12 13"],
        "B", "Closures",
        "Late binding: i is looked up when lambda runs; final i=2 for all."
    ))
    B.append(q(
        "How do you fix the late-binding issue in the previous pattern?",
        ["Use global i", "Use default arg like lambda x, i=i: x+i", "Use eval()", "Use list.sort()"],
        "B", "Closures"
    ))
    B.append(q(
        "What does this print?\n\nx = {'a': 1}\nprint(list(x))",
        ["['a']", "['a', 1]", "[('a',1)]", "TypeError"],
        "A", "Data Structures",
        "Iterating a dict yields keys."
    ))
    B.append(q(
        "What is printed?\n\nprint(list(zip([1,2,3], ['a','b'])))",
        ["[(1,'a'), (2,'b')]", "[(1,'a'), (2,'b'), (3,None)]", "TypeError", "[(1,'a'), (2,'b'), (3,'c')]"],
        "A", "Stdlib",
        "zip stops at the shortest input."
    ))
    B.append(q(
        "What is printed?\n\nprint(list(map(lambda x: x*x, [1,2,3])))",
        ["[1,4,9]", "[1,2,3]", "<map object ...>", "TypeError"],
        "A", "Stdlib"
    ))
    B.append(q(
        "What happens?\n\ns = 'abc'\ns[0] = 'z'",
        ["Works, s becomes 'zbc'", "TypeError", "ValueError", "IndexError"],
        "B", "Strings",
        "Strings are immutable."
    ))
    B.append(q(
        "What prints?\n\ndef f(a, b, /, c):\n    return a, b, c\n\nprint(f(1, 2, c=3))",
        ["(1,2,3)", "TypeError", "(1,2,'c')", "SyntaxError"],
        "A", "Functions",
        "'/' makes a,b positional-only; c can be keyword."
    ))
    B.append(q(
        "What does this print?\n\nprint(isinstance(True, int))",
        ["True", "False", "TypeError", "Depends on version"],
        "A", "Basics",
        "bool is a subclass of int in Python."
    ))
    B.append(q(
        "What is printed?\n\nprint({i for i in [1,2,2,3] if i % 2})",
        ["{1, 3}", "{1,2,3}", "{2}", "[]"],
        "A", "Comprehensions"
    ))
    B.append(q(
        "What does this print?\n\nd = {'a': 1, 'b': 2}\nprint(list(d.items()))",
        ["['a','b']", "[('a',1), ('b',2)]", "[1,2]", "TypeError"],
        "B", "Data Structures"
    ))
    B.append(q(
        "What does this print?\n\nprint('a' < 'B')",
        ["True", "False", "TypeError", "Depends on locale"],
        "B", "Strings",
        "Comparison is by Unicode code point; uppercase letters come before lowercase."
    ))
    B.append(q(
        "Which are TRUE about list slicing? (Select ALL that apply)",
        ["Slicing returns a new list", "Slicing can be used to replace part of a list", "Slicing always deep-copies nested objects", "Slicing supports step"],
        "A,B,D", "Sequences"
    ))
    B.append(q(
        "What is printed?\n\nx = [1,2,3]\nx[1:2] = [9,9]\nprint(x)",
        ["[1,9,9,3]", "[1,9,3]", "[9,9]", "TypeError"],
        "A", "Sequences"
    ))
    B.append(q(
        "What is printed?\n\nx = [1,2,3]\nx[1:1] = [9]\nprint(x)",
        ["[1,9,2,3]", "[1,2,3,9]", "[1,2,9,3]", "TypeError"],
        "A", "Sequences",
        "Slice assignment at empty slice inserts."
    ))
    B.append(q(
        "What does this print?\n\nprint(any([0, '', None, 5]))",
        ["True", "False", "TypeError", "None"],
        "A", "Stdlib"
    ))
    B.append(q(
        "What does this print?\n\nprint(all([1, 'x', [], 3]))",
        ["True", "False", "TypeError", "Depends on order"],
        "B", "Stdlib",
        "[] is falsy so all(...) is False."
    ))
    B.append(q(
        "What does this print?\n\ndef f():\n    for i in range(3):\n        yield i\n\ng = f()\nprint(next(g), next(g))",
        ["0 1", "1 2", "0 2", "StopIteration"],
        "A", "Iterators/Generators"
    ))
    B.append(q(
        "What is printed?\n\nprint(list(reversed([1,2,3])))",
        ["[3,2,1]", "[1,2,3]", "<reversed object ...>", "TypeError"],
        "A", "Stdlib"
    ))
    B.append(q(
        "Which is TRUE about 'is' with small integers?",
        ["It always returns True for equal ints", "It may return True due to interning/caching but should not be relied on for value equality", "It is guaranteed False", "It raises TypeError"],
        "B", "Pitfalls"
    ))
    B.append(q(
        "What does this print?\n\nprint({} == dict())",
        ["True", "False", "TypeError", "Depends on CPython"],
        "A", "Basics"
    ))
    B.append(q(
        "Which are TRUE about Python's 'finally'? (Select ALL that apply)",
        ["It runs if no exception occurs", "It runs if an exception occurs", "It always runs even if process is killed by OS", "It can override a pending exception if it raises another exception"],
        "A,B,D", "Exceptions",
        "Finally usually runs, but not in all abrupt termination scenarios."
    ))

    # Bank is intentionally > 110 by duplicating NOTHING; add more unique items:
    B.extend([
        q("What prints?\n\nprint(' '.join(['hi', 'there']))",
          ["hi there", "hithere", "['hi','there']", "TypeError"], "A", "Strings"),
        q("What prints?\n\nprint('hi\\nthere'.splitlines())",
          ["['hi there']", "['hi', 'there']", "['hi\\nthere']", "TypeError"], "B", "Strings"),
        q("What prints?\n\nprint(list(filter(None, [0, 1, '', 'a'])))",
          ["[0, 1, '', 'a']", "[1, 'a']", "['a']", "TypeError"], "B", "Stdlib"),
        q("What is printed?\n\nx = [1,2,3]\nprint(x[-1])",
          ["1", "2", "3", "IndexError"], "C", "Sequences"),
        q("Which is TRUE about list.append vs list.extend?",
          ["append adds items individually; extend adds as one element",
           "append adds one element; extend iterates and adds elements",
           "Both are identical", "extend only works for sets"], "B", "Data Structures"),
        q("What does this print?\n\nprint({1,2} | {2,3})",
          ["{1,2,3}", "{2}", "{1,2} and {2,3}", "TypeError"], "A", "Data Structures"),
        q("What does this print?\n\nprint({1,2,3} & {2,4})",
          ["{1,2,3,4}", "{2}", "{1,4}", "TypeError"], "B", "Data Structures"),
        q("What is printed?\n\nprint([i*i for i in range(4) if i%2==0])",
          ["[0, 4]", "[1, 9]", "[0, 1, 4, 9]", "[2]"], "A", "Comprehensions"),
        q("Which statement about recursion in Python is TRUE?",
          ["Tail-call optimization prevents stack growth", "Python limits recursion depth by default", "Recursion is always faster than loops", "Recursion cannot return values"], "B", "Basics"),
        q("What is printed?\n\nprint(type(lambda x: x))",
          ["function", "<class 'function'>", "<lambda>", "callable"], "B", "Functions"),
        q("What does this print?\n\nprint((lambda x: x+1)(5))",
          ["5", "6", "Error", "None"], "B", "Functions"),
        q("What does this print?\n\nx = {'a': 1}\nprint(x.pop('a'), x)",
          ["1 {}", "{} 1", "KeyError", "None {}"], "A", "Data Structures"),
        q("What prints?\n\nimport math\nprint(math.isclose(0.1+0.2, 0.3))",
          ["True", "False", "TypeError", "Depends on locale"], "A", "Numerics"),
        q("What is printed?\n\nprint(list(range(10))[1:8:3])",
          ["[1,4,7]", "[1,3,5,7]", "[2,5,8]", "[1,8]"], "A", "Sequences"),
        q("Which are TRUE about 'set' iteration order?",
          ["Always sorted", "Deterministic across runs", "Not guaranteed sorted; depends on hashing", "Guaranteed insertion order"], "C", "Data Structures"),
        q("In Python 3.7+, dict preserves:",
          ["Sorted order", "Insertion order (as a language guarantee)", "Random order", "Reverse insertion order"], "B", "Data Structures"),
        q("What happens?\n\ntry:\n    raise ValueError('x')\nexcept Exception as e:\n    print(type(e).__name__)",
          ["ValueError", "Exception", "Error", "TypeError"], "A", "Exceptions"),
        q("What is printed?\n\nprint('%.2f' % 1.239)",
          ["1.23", "1.24", "1.239", "TypeError"], "B", "Strings"),
        q("What does this print?\n\nprint(f\"{2+3} \")",
          ["5", "2+3", "Error", "5 "], "D", "Strings"),
        q("Which are TRUE about '==' for lists? (Select ALL that apply)",
          ["Compares by identity", "Compares element values in order", "Lists of different lengths can be equal", "Nested lists are compared recursively by value"], "B,D", "Data Structures"),
        q("What is printed?\n\nprint([1,2] == [1,2], [1,2] is [1,2])",
          ["True True", "True False", "False True", "False False"], "B", "References"),
        q("What is printed?\n\nx = None\nprint(x is None)",
          ["True", "False", "TypeError", "Depends"], "A", "Basics"),
        q("Which is a correct way to handle a possibly-missing dict key 'k'?",
          ["d.k", "d['k'] without try", "d.get('k')", "d.k()"], "C", "Data Structures"),
        q("What is printed?\n\nprint(min(['aa','b','ccc'], key=len))",
          ["aa", "b", "ccc", "TypeError"], "B", "Stdlib"),
        q("What does this print?\n\nprint(list({1: 'a', 2: 'b'}.values()))",
          ["[1,2]", "['a','b']", "[(1,'a'), (2,'b')]", "TypeError"], "B", "Data Structures"),
        q("What does this print?\n\nprint({k:v for k,v in [('a',1), ('b',2)]})",
          ["{'a':1,'b':2}", "[('a',1), ('b',2)]", "{('a',1), ('b',2)}", "TypeError"], "A", "Comprehensions"),
        q("Which tool is used to create an immutable set?",
          ["set()", "frozenset()", "tuple()", "immutableset()"], "B", "Data Structures"),
        q("What is printed?\n\nprint(type(frozenset([1,2])))",
          ["set", "frozenset", "<class 'frozenset'>", "TypeError"], "C", "Data Structures"),
    ])

    # Sanity: require 80+ unique questions
    assert len(B) >= 110, f"Bank too small: {len(B)}"
    return B


def pick_exam(bank: List[Question], n: int) -> List[Question]:
    # Ensure topic variety: lightly balance by topic
    by_topic: Dict[str, List[Question]] = {}
    for qu in bank:
        by_topic.setdefault(qu.topic, []).append(qu)

    # Shuffle each topic bucket
    for lst in by_topic.values():
        random.shuffle(lst)

    topics = list(by_topic.keys())
    random.shuffle(topics)

    exam: List[Question] = []
    # Round-robin topics to improve diversity
    while len(exam) < n:
        made_progress = False
        for t in topics:
            if by_topic[t]:
                exam.append(by_topic[t].pop())
                made_progress = True
                if len(exam) == n:
                    break
        if not made_progress:
            break

    # If still short (shouldn't happen), fill randomly
    if len(exam) < n:
        remaining = [x for xs in by_topic.values() for x in xs]
        random.shuffle(remaining)
        exam.extend(remaining[: (n - len(exam))])

    return exam[:n]


def run_exam(bank: List[Question]) -> None:
    exam = pick_exam(bank, TOTAL_QUESTIONS)
    start = time.time()

    correct = 0
    per_topic: Dict[str, Tuple[int, int]] = {}  # topic -> (correct, total)
    missed: List[Tuple[Question, Set[int]]] = []

    print("\nPython 3 Practice Assessment (original questions)")
    print(f"Questions: {TOTAL_QUESTIONS}")
    print(f"Time limit: {TIME_LIMIT_SECONDS // 60} minutes")
    print("Answer format: A (single) or A,C (multi-select). Type 'q' to quit.\n")

    for i, qu in enumerate(exam, start=1):
        remaining = time_left(start)
        if remaining <= 0:
            print("\nTime is up!")
            break

        print("=" * 78)
        print(f"Q{i}/{TOTAL_QUESTIONS}  |  Topic: {qu.topic}  |  Time left: {fmt_mmss(remaining)}\n")
        print(qu.prompt)
        print()

        for idx, opt in enumerate(qu.options):
            print(f"  {LETTERS[idx]}. {opt}")

        print("\n(Select ALL that apply)" if qu.multi_select else "\n(Select ONE answer)")

        while True:
            remaining = time_left(start)
            if remaining <= 0:
                print("\nTime is up!")
                break

            raw = input("Your answer: ")
            chosen = parse_answer(raw, qu.multi_select, len(qu.options))
            if chosen is None:
                print("Invalid input. Example: A  or  A,C")
                continue
            if -1 in chosen:
                print("\nExiting exam early.")
                show_results(correct, per_topic, missed, attempted=i - 1)
                return

            is_correct = chosen == qu.correct

            c, t = per_topic.get(qu.topic, (0, 0))
            per_topic[qu.topic] = (c + (1 if is_correct else 0), t + 1)

            if is_correct:
                correct += 1
                print("Correct!\n")
            else:
                missed.append((qu, chosen))
                print(f"Incorrect. Correct: {idxs_to_letters(qu.correct)}\n")
            break

        if time_left(start) <= 0:
            break

    attempted = sum(t for _, t in per_topic.values())
    show_results(correct, per_topic, missed, attempted=attempted)


def show_results(correct: int, per_topic: Dict[str, Tuple[int, int]],
                 missed: List[Tuple[Question, Set[int]]], attempted: int) -> None:
    print("\n" + "=" * 78)
    print("RESULTS")
    print("=" * 78)
    if attempted == 0:
        print("No questions attempted.")
        return

    pct = (correct / attempted) * 100.0
    print(f"Attempted: {attempted}")
    print(f"Correct:   {correct}")
    print(f"Score:     {pct:.1f}%\n")

    print("Topic breakdown:")
    rows = []
    for topic, (c, t) in per_topic.items():
        rows.append((t, (c / t) * 100.0, topic, c))
    rows.sort(key=lambda x: (-x[0], x[1]))

    for t, tpct, topic, c in rows:
        print(f"  {topic:20s}  {c:2d}/{t:2d}  ({tpct:5.1f}%)")

    if REVIEW_MISSED_AT_END and missed:
        print("\n" + "-" * 78)
        print("Review missed questions")
        print("-" * 78)
        for idx, (qu, chosen) in enumerate(missed, start=1):
            print(f"\nMissed #{idx} | Topic: {qu.topic}")
            print(qu.prompt)
            for i, opt in enumerate(qu.options):
                marker = ""
                if i in qu.correct:
                    marker += "  [CORRECT]"
                print(f"  {LETTERS[i]}. {opt}{marker}")
            print(f"Your answer: {idxs_to_letters(chosen)}")
            if qu.explanation:
                print(f"Why: {qu.explanation}")

    print("\nTip: run again for a different balanced set of 54.\n")


def main() -> int:
    random.seed()  # system time
    bank = build_bank()
    if len(bank) < TOTAL_QUESTIONS:
        print("Question bank too small.")
        return 1
    run_exam(bank)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

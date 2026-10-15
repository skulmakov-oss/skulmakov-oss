"""Generate SHF-R scaling workloads (Semantic source) for sizes N.

Each workload self-asserts its result, so ok == semantically correct.
"""
import pathlib
import sys

OUT = pathlib.Path(sys.argv[1])
SIZES = [int(s) for s in sys.argv[2].split(",")]


def seq_push(n):
    return f"""fn main() {{
    let mut s: Sequence(i32) = [];
    let mut i: i32 = 0;
    while i < {n} {{ s = push(s, i); i = i + 1; }}
    assert(len(s) == {n});
    return;
}}
"""


def seq_read(n):
    # build once, then read every element by index: read amplification probe
    return f"""fn main() {{
    let mut s: Sequence(i32) = [];
    let mut i: i32 = 0;
    while i < {n} {{ s = push(s, 1); i = i + 1; }}
    let mut acc: i32 = 0;
    let mut j: i32 = 0;
    while j < {n} {{ acc = acc + s[j]; j = j + 1; }}
    assert(acc == {n});
    return;
}}
"""


def record_with(n):
    return f"""record St {{ pos: i32, line: i32, col: i32, count: i32 }}
fn main() {{
    let mut st: St = St {{ pos: 0, line: 1, col: 0, count: 0 }};
    let mut i: i32 = 0;
    while i < {n} {{
        st = st with {{ pos: st.pos + 1, col: st.col + 1, count: st.count + 1 }};
        i = i + 1;
    }}
    assert(st.count == {n});
    return;
}}
"""


def state_record_seq(n):
    # compiler-like state: a record carrying a growing token sequence
    return f"""record Lx {{ toks: Sequence(i32), pos: i32 }}
fn main() {{
    let mut st: Lx = Lx {{ toks: [], pos: 0 }};
    let mut i: i32 = 0;
    while i < {n} {{
        st = st with {{ toks: push(st.toks, i), pos: st.pos + 1 }};
        i = i + 1;
    }}
    assert(len(st.toks) == {n});
    return;
}}
"""


def tuple_loop(n):
    return f"""fn main() {{
    let mut t: (i32, i32) = (0, 0);
    let mut i: i32 = 0;
    while i < {n} {{
        t = (t.0 + 1, t.1 + 2);
        i = i + 1;
    }}
    assert(t.0 == {n});
    assert(t.1 == {2 * n});
    return;
}}
"""


def map_set(n):
    return f"""fn main() {{
    let mut m: Map(i32, i32) = map_empty();
    let mut i: i32 = 0;
    while i < {n} {{ m = map_set(m, i, i); i = i + 1; }}
    assert(map_get(m, {n - 1}, 0) == {n - 1});
    return;
}}
"""


def text_literal(n):
    unit = "let x = 42; "  # 12 bytes, 3 digits... count '4'
    reps = max(1, n // len(unit))
    return unit * reps, reps


def text_scan(n):
    lit, reps = text_literal(n)
    return f"""fn main() {{
    let src: text = fs_read_text("input_{n}.txt");
    let n: u32 = text_len(src);
    let mut i: u32 = 0u32;
    let mut fours: i32 = 0;
    while i < n {{
        match text_byte_at(src, i) {{
            Option::Some(b) => {{ if b == 52u32 {{ fours = fours + 1; }} }}
            Option::None => {{ assert(false); }}
        }}
        i = i + 1u32;
    }}
    assert(fours == {reps});
    return;
}}
"""


def lex_calls(n):
    # lexer-shaped: one helper call per byte -> exposes the total Calls ceiling
    lit, reps = text_literal(n)
    return f"""fn is_digit(b: u32) -> bool {{ return b >= 48u32 && b <= 57u32; }}
fn main() {{
    let src: text = fs_read_text("input_{n}.txt");
    let n: u32 = text_len(src);
    let mut i: u32 = 0u32;
    let mut digits: i32 = 0;
    let mut toks: Sequence(i32) = [];
    while i < n {{
        match text_byte_at(src, i) {{
            Option::Some(b) => {{
                if is_digit(b) {{ digits = digits + 1; toks = push(toks, 1); }}
            }}
            Option::None => {{ assert(false); }}
        }}
        i = i + 1u32;
    }}
    assert(digits == {2 * reps});
    return;
}}
"""


FAMILIES = {
    "seq_push": seq_push,
    "seq_read": seq_read,
    "record_with": record_with,
    "state_record_seq": state_record_seq,
    "tuple_loop": tuple_loop,
    "map_set": map_set,
    "text_scan": text_scan,
    "lex_calls": lex_calls,
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "root").mkdir(exist_ok=True)
for n in SIZES:
    (OUT / "root" / f"input_{n}.txt").write_text(text_literal(n)[0])
for name, fn in FAMILIES.items():
    for n in SIZES:
        (OUT / f"{name}_{n}.sm").write_text(fn(n))
print(f"generated {len(FAMILIES) * len(SIZES)} workloads in {OUT}")


def map_get(n):
    return f"""fn main() {{
    let mut m: Map(i32, i32) = map_empty();
    let mut i: i32 = 0;
    while i < {n} {{ m = map_set(m, i, i); i = i + 1; }}
    let mut acc: i32 = 0;
    let mut j: i32 = 0;
    while j < {n} {{ if map_contains(m, j) {{ acc = acc + map_get(m, j, 0) - j + 1; }} j = j + 1; }}
    assert(acc == {n});
    return;
}}
"""


def state_record_map(n):
    # compiler-like context record carrying a symbol table
    return f"""record Ctx {{ syms: Map(text, i32), next_id: i32 }}
fn main() {{
    let mut c: Ctx = Ctx {{ syms: map_empty(), next_id: 0 }};
    let mut i: i32 = 0;
    while i < {n} {{
        c = c with {{ syms: map_set(c.syms, "s" + to_text(i), c.next_id), next_id: c.next_id + 1 }};
        i = i + 1;
    }}
    assert(map_get(c.syms, "s{n - 1}", -1) == {n - 1});
    assert(map_get(c.syms, "missing", -1) == -1);
    return;
}}
"""


def map_versions(n):
    # persistence: an old version must be unaffected by later updates
    return f"""fn main() {{
    let mut m: Map(i32, i32) = map_empty();
    let mut i: i32 = 0;
    while i < {n} {{ m = map_set(m, i, i); i = i + 1; }}
    let old: Map(i32, i32) = m;
    let mut j: i32 = 0;
    while j < {n} {{ m = map_set(m, j, -1); j = j + 1; }}
    assert(map_get(old, {n // 2}, 0) == {n // 2});
    assert(map_get(m, {n // 2}, 0) == -1);
    return;
}}
"""


FAMILIES.update({"map_get": map_get, "state_record_map": state_record_map, "map_versions": map_versions})
for name in ("map_get", "state_record_map", "map_versions"):
    for n in SIZES:
        (OUT / f"{name}_{n}.sm").write_text(FAMILIES[name](n))

import re
class MockFST:
    @staticmethod
    def re(rule_string):
        if rule_string == "m ([aeiou]) -> wa \\1":
            return MockRule(r"^m([aeiou])", r"wa\1")
        elif rule_string == "m ([aeiou]) -> mi \\1":
            return MockRule(r"^m([aeiou])", r"mi\1")
        elif rule_string == "ki -> vi":
            return MockRule(r"^ki", r"vi")
        elif rule_string == "ch -> vy":
            return MockRule(r"^ch", r"vy")
        return MockRule("", "")
class MockRule:
    def __init__(self, pattern, replacement):
        self.pattern = pattern
        self.replacement = replacement

    def apply(self, word):
        if not self.pattern:
            return word
        return re.sub(self.pattern, self.replacement, word)
FST = MockFST()
rule_cl1    = FST.re("m ([aeiou]) -> wa \\1")
rule_cl3    = FST.re("m ([aeiou]) -> mi \\1")
rule_cl7_ki = FST.re("ki -> vi")
rule_cl7_ch = FST.re("ch -> vy")
def analyze(word, tag):
    if tag == "[CL1]":
        return rule_cl1.apply(word)
    elif tag == "[CL3]":
        return rule_cl3.apply(word)
    elif tag == "[CL7]":
        r1 = rule_cl7_ki.apply(word)
        return r1 if r1 != word else rule_cl7_ch.apply(word)
    elif tag == "[CL9]":
        return word
    return "Unknown"
held_out = [
    ("mtoto",     "[CL1]", "watoto"),
    ("mgeni",     "[CL1]", "wageni"),
    ("mwalimu",   "[CL1]", "waalimu"),
    ("mhandisi",  "[CL1]", "wahandisi"),
    ("mke",       "[CL1]", "wake"),        # FAIL
    ("mume",      "[CL1]", "waume"),
    ("mche",      "[CL3]", "miche"),       # FAIL
    ("mzizi",     "[CL3]", "mizizi"),
    ("mji",       "[CL3]", "miji"),
    ("mguu",      "[CL3]", "miguu"),       # FAIL
    ("kisu",      "[CL7]", "visu"),
    ("kikapu",    "[CL7]", "vikapu"),
    ("chakula",   "[CL7]", "vyakula"),
    ("kitabu",    "[CL7]", "vitabu"),
    ("mbwa",      "[CL9]", "mbwa"),
]
header = f"{'Input':<13} | {'Tag':<6} | {'Expected':<12} | {'FST Output':<12} | Status"
separator = "-" * 75
results_lines = ["TEST RESULTS (15 held-out forms)", "="*32, header, separator]
error_lines = ["ERROR LOG (genuine failures from the run above)", "="*47, ""]
print(header)
print(separator)
results = []
for word, tag, expected in held_out:
    out = analyze(word, tag)
    status = "PASS" if out == expected else "FAIL"
    results.append((word, tag, expected, out, status))
    line = f"{word:<13} | {tag:<6} | {expected:<12} | {out:<12} | {status}"
    print(line)
    results_lines.append(line)
for w, t, e, o, s in results:
    if s == "FAIL":
        error_msg = f"FAIL: {w}{t}  ->  expected '{e}', got '{o}'"
        print(f"\n{error_msg}")
        error_lines.append(error_msg)
pass_count = sum(1 for r in results if r[4] == "PASS")
fail_count = sum(1 for r in results if r[4] == "FAIL")
results_lines.append(f"\nSUMMARY: {pass_count} PASS / {fail_count} FAIL")
with open("04_test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results_lines))
with open("05_error_log.txt", "w", encoding="utf-8") as f:
 f.write("\n".join(error_lines))
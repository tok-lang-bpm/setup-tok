"""Check the models named by TOK_CHECK with tok and report the diagnostics as annotations.

Every diagnostic becomes an annotation on its line of the file (errors as errors, warnings as
warnings, notes as notices); the step summary gets a table of the files. The step fails when
a model has errors, or, with TOK_FAIL_ON=warning, warnings.
"""

import glob
import json
import os
import subprocess
import sys

LEVEL = {"error": "error", "warning": "warning", "note": "notice"}


def escape(text):
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def prop(text):
    return escape(text).replace(":", "%3A").replace(",", "%2C")


def main():
    pattern = os.environ.get("TOK_CHECK", "**/*.tok")
    lang = os.environ.get("TOK_LANG", "en")
    fail_on = os.environ.get("TOK_FAIL_ON", "error")
    if lang not in ("en", "pl"):
        print("::error title=setup-tok::lang must be en or pl, not %s" % lang)
        return 2
    if fail_on not in ("error", "warning"):
        print("::error title=setup-tok::fail-on must be error or warning, not %s" % fail_on)
        return 2
    files = sorted(f for f in glob.glob(pattern, recursive=True) if os.path.isfile(f))
    rows = []
    errors = warnings = 0
    for path in files:
        r = subprocess.run(["tok", "check", path, "--json", "--lang", lang],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            report = json.loads(r.stdout.decode("utf-8"))
        except ValueError:
            message = (r.stderr or r.stdout).decode("utf-8", "replace").strip()
            print("::error file=%s,title=tok::%s" % (prop(path), escape(message)))
            errors += 1
            rows.append((path, 1, 0, 0))
            continue
        e = w = n = 0
        for d in report.get("diagnostics", []):
            sev = d.get("severity", "note")
            e += sev == "error"
            w += sev == "warning"
            n += sev == "note"
            where = "file=%s" % prop(path)
            if d.get("line"):
                where += ",line=%d" % d["line"]
            print("::%s %s,title=%s::%s" % (LEVEL.get(sev, "notice"), where,
                                             prop(d.get("code", "tok")),
                                             escape(d.get("message", ""))))
        errors += e
        warnings += w
        rows.append((path, e, w, n))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### tok check\n\n")
            if rows:
                f.write("| Model | Errors | Warnings | Notes |\n|---|---|---|---|\n")
                for path, e, w, n in rows:
                    f.write("| `%s` | %d | %d | %d |\n" % (path, e, w, n))
            else:
                f.write("No file matches `%s`.\n" % pattern)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write("errors=%d\nwarnings=%d\n" % (errors, warnings))
    print("%d model(s) checked: %d error(s), %d warning(s)" % (len(files), errors, warnings))
    if errors or (fail_on == "warning" and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

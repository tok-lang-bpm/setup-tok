# setup-tok

A GitHub Action that installs [tok](https://github.com/tok-lang-bpm/tok), the plain-text language for BPMN 2.0 process models and DMN decisions, and checks the models of your repository. Every diagnostic of `tok check` appears as an annotation on its line of the `.tok` file, the job summary lists the checked files, and the step fails when a model has errors.

```yaml
name: models
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: tok-lang-bpm/setup-tok@v1
        with:
          check: "models/**/*.tok"
      - run: tok export models/loan.tok -o build/     # tok stays on the PATH
      - uses: actions/upload-artifact@v4
        with:
          name: bpmn
          path: build/
```

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `version` | the latest | version of the Python package `tok-lang` to install, for example `1.0.3` |
| `check` | `**/*.tok` | glob of the models to check (`**` matches any folder): tok documents, or BPMN 2.0 XML files from any modelling tool (`**/*.bpmn`, checked with the BPMN rules of tok 1.0.3 or newer); an empty string only installs tok |
| `lang` | `en` | language of the diagnostics: `en` or `pl` |
| `fail-on` | `error` | `error`: the step fails when a model has errors; `warning`: also when it has warnings |

## Outputs

| Output | Meaning |
|---|---|
| `version` | the installed version of tok |
| `errors` | the number of errors in the checked models |
| `warnings` | the number of warnings in the checked models |

The action needs Python 3.8 or newer on the runner (the GitHub-hosted runners have it). It installs tok in a virtual environment of its own and adds it to the `PATH`, so later steps can run `tok fmt --check`, `tok bpmn`, `tok svg`, `tok export` or `tok sim`.

The same check runs in any other CI (Forgejo Actions, GitLab CI, Jenkins): `pip install tok-lang`, then `tok check MODEL.tok` for each model; the exit code is 1 when a model has errors.

## Licence

GNU General Public License v3.0 or later, as tok. Issues: https://github.com/tok-lang-bpm/tok/issues.

# ec_utils (originally eurocalliopelib)

Utility code for the `ec_modules`.

Contains general-purpose functions and routines that we expect to change at a slow pace. Think of this as any other dependency in your workflow.

To use it, add the following to the relevant `environment.yaml` in your module:

```yaml
name: your-environment
channels:
  - conda-forge
  - nodefaults
dependencies:
  - pip
  - pip:
    - "git+https://github.com/calliope-project/ec_utils.git@v0.1.0"
```

## Development

We recommend using `mamba` for development.

```bash
mamba create -n ec_utils --file requirements/base.txt --file requirements/geo.txt --file requirements/dev.txt
mamba activate ec_utils
pip install --no-deps -e .
```

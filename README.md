<<<<<<< HEAD
hello world this is Alexa




=======
# pyglmbayes

Bayesian generalized linear models with **exact independent and identically distributed (iid) posterior sampling** — a Python port of the R package [glmbayes](https://cran.r-project.org/package=glmbayes).

## Status

This project is in **early development**. The package layout and APIs described below are the design targets; implementation is not yet complete. See [pyproject.toml](pyproject.toml) for current dependencies and version.

## Why pyglmbayes?

The R package **glmbayes** provides iid samples from Bayesian GLM posteriors for log-concave likelihoods, using accept–reject sampling based on likelihood subgradients (Nygren and Nygren, 2006). That differs from approximate Bayesian GLM approaches (for example `arm::bayesglm()`), which use iterative approximations rather than exact iid draws where the theory applies.

**pyglmbayes** brings those algorithms to Python with two goals:

1. **Faithful R interoperability** — an interface that mirrors `glmb()`, `lmb()`, and related glmbayes workflows so R users and existing analyses can port with minimal friction.
2. **Idiomatic Python GLM workflows** — an interface aligned with the ecosystem built around [statsmodels](https://www.statsmodels.org/) (formula specification, `family` objects, and familiar `fit` / `summary` patterns), extended with Bayesian posterior sampling and summaries.

The core sampling engine is also intended to serve as a **computational backend** for higher-level Python packages that need glmbayes-style inference without reimplementing the samplers.

## Features (planned)

- Exact **iid posterior sampling** for Bayesian GLMs with log-concave likelihoods
- Support for major GLM families (Gaussian, binomial, Poisson, Gamma, and quasi variants where applicable in the R package)
- Flexible **prior specification** via objects analogous to R’s `pfamily` and prior-setup utilities
- **Two user-facing APIs** over a shared core (see [Architecture](#architecture))
- **Gaussian fast path** via an `lmb`-style interface (Bayesian analogue of linear models)
- Posterior summaries, diagnostics, and prediction hooks consistent across both interfaces

## Installation

Requires **Python ≥ 3.10**.

From a clone of this repository (editable install for development):

```bash
python -m pip install -e ".[dev]"
```

When published to PyPI:

```bash
python -m pip install pyglmbayes
```

Optional extras for the statsmodels-style interface (formula API, family bridging) will be documented here as they are added to `pyproject.toml`.

## Quick start

Examples below illustrate **intended** usage once the port is implemented; they are not runnable yet.

### R-style API

For users coming from glmbayes in R:

```python
import pyglmbayes as pgb
import pandas as pd

df = pd.read_csv("mydata.csv")

# Prior setup (analogous to Prior_Setup() in R)
prior = pgb.prior_setup(
    family=pgb.families.Gaussian(),
    prior_type="dNormal",
    # ... prior hyperparameters ...
)

# Bayesian GLM — analogue of glmb()
fit = pgb.glmb(
    formula="y ~ x1 + x2",
    data=df,
    pfamily=prior,
    n_samples=1000,
)

print(fit.coef())              # posterior summaries for coefficients
samples = fit.posterior_draws()  # iid sample matrix
```

Gaussian models can use the **`lmb`** shortcut (Bayesian analogue of R’s `lm()`):

```python
fit = pgb.lmb("y ~ x1 + x2", data=df, prior=prior, n_samples=1000)
```

### Python GLM API (statsmodels-style)

For users who prefer formula + `family` + `fit()`:

```python
import pandas as pd
import pyglmbayes as pgb

df = pd.read_csv("mydata.csv")

model = pgb.BayesGLM.from_formula(
    "y ~ x1 + x2",
    data=df,
    family=pgb.families.Binomial(),
    prior=pgb.priors.default(),  # or explicit prior object
)
result = model.fit(n_samples=1000)

result.summary()                 # table-style summary (statsmodels-like)
result.fittedvalues
result.posterior_samples()       # Bayesian draws
```

Both paths call the same underlying sampler and return objects that share core posterior data; only the specification and convenience methods differ.

## Supported models

Coverage will follow the R package, which focuses on **log-concave** likelihoods and efficient iid sampling. The table below summarizes the main cases documented for [glmbayes](https://cran.r-project.org/web/packages/glmbayes/readme/README.html); quasi-likelihood and models with unknown dispersion may use Gibbs or other extensions as in the R vignettes.

| Likelihood | Example links | Prior notes (examples) |
|------------|---------------|-------------------------|
| Gaussian | identity | Normal, Normal–Gamma, independent Normal–Gamma |
| Poisson | log | Priors via `pfamily` |
| Binomial / quasi-binomial | logit | Priors via `pfamily` |
| Gamma | log | Dispersion: fixed or Gibbs extensions (see R Chapter 11) |

For theory, examples, and prior details, see the [glmbayes vignettes](https://cran.r-project.org/web/packages/glmbayes/vignettes/) on CRAN.

## Architecture

```text
                    ┌─────────────────────────┐
                    │  Higher-level package   │  (optional consumer)
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
     ┌─────────────────┐               ┌─────────────────┐
     │   R-like API    │               │  BayesGLM API   │
     │ glmb, lmb,      │               │ formula +       │
     │ pfamily, …      │               │ family + fit    │
     └────────┬────────┘               └────────┬────────┘
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │  Core: priors + iid     │
                    │  accept–reject /        │
                    │  subgradient sampling   │
                    └─────────────────────────┘
```

- **Core** — prior objects, likelihoods, and iid samplers (NumPy/SciPy).
- **R-like layer** — argument names and workflows aligned with glmbayes.
- **Python GLM layer** — statsmodels-oriented construction and result objects.
- **Backend use** — downstream packages may import core routines or either façade directly.

## Relationship to glmbayes (R)

| Topic | R (glmbayes) | Python (pyglmbayes) |
|-------|----------------|----------------------|
| Primary GLM entry | `glmb()` | `glmb()` / `BayesGLM` |
| Linear Gaussian entry | `lmb()` | `lmb()` / Gaussian `BayesGLM` |
| Priors / likelihood | `pfamily`, `Prior_Setup()` | `pfamily`, `prior_setup()` (names may adjust slightly) |
| Inference | Exact iid samples (log-concave cases) | Same algorithms (port) |
| Reference docs | CRAN README + vignettes | This README + future docs |

We aim for **numerical and API parity where practical**, with Pythonic naming and packaging where R conventions do not fit.

## Development

```bash
git clone https://github.com/<your-org>/pyglmbayes.git
cd pyglmbayes
python -m pip install -e ".[dev]"
python -m pytest
```

Package source will live under `src/pyglmbayes/` (see [pyproject.toml](pyproject.toml)).

## Roadmap

- [ ] Core sampler and `pfamily` / prior layer
- [ ] R-like `glmb` and `lmb`
- [ ] statsmodels-style `BayesGLM` and result objects
- [ ] Parity tests against R glmbayes on reference datasets
- [ ] Documentation and vignette-style examples

## Citation

If you use this software, please cite the original **glmbayes** R package and the underlying methodology (Nygren and Nygren, 2006). Citation details for the Python port will be added when the first release is published.

## License

License to be specified (align with the R package and repository policy).

## References

- Nygren, K. J., and Nygren, A. A. (2006). *Likelihood subgradient densities for Bayesian inference.* (Sampling methodology used in glmbayes.)
- [glmbayes on CRAN](https://cran.r-project.org/package=glmbayes)
- Gelman, A., et al. (2013). *Bayesian Data Analysis.* (General Bayesian GLM background, as in R vignettes.)
>>>>>>> 284dc02e6b22c47bcd7d299e73724de09df09ea6

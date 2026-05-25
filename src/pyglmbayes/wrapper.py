"""Draft helpers for temporarily wrapping model fit callables."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

BeforeHook = Callable[..., None]
AfterHook = Callable[[Any], None]


def wrap_function(
    fn: F,
    *,
    before: BeforeHook | None = None,
    after: AfterHook | None = None,
) -> F:
    """Return a temporary wrapper around ``fn`` with optional hooks.

    Use this to add logging, timing, or inspection around an existing fit
    function without changing its implementation. Typical targets are
    statsmodels-style ``.fit()`` callables or package entry points such as
    ``BayesGLM.fit`` once those exist.

    Parameters
    ----------
    fn:
        Callable to wrap (for example ``model.fit`` or a helper that builds
        and fits a GLM).
    before:
        Called with the same ``*args`` and ``**kwargs`` passed to ``fn``.
    after:
        Called with the return value of ``fn``.

    Returns
    -------
    A wrapped callable that preserves ``fn``'s name and docstring.

    Examples
    --------
    Wrap a statsmodels fit for quick debugging::

        import statsmodels.formula.api as smf

        model = smf.glm("y ~ x1 + x2", data=df, family=sm.families.Binomial())
        fit = wrap_function(
            model.fit,
            before=lambda *a, **k: print("fit kwargs:", k),
            after=lambda result: print(result.summary()),
        )
        result = fit()
    """
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if before is not None:
            before(*args, **kwargs)
        result = fn(*args, **kwargs)
        if after is not None:
            after(result)
        return result

    return wrapper  # type: ignore[return-value]

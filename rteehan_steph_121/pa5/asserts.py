# CS122 Linear regression
#
# Validity checkers to make functions in model.py return more
# user-friendly errors.
import numpy as np


class Asserter:
    """
    Helper functor to test assertions.
    """
    def __init__(self, fname):
        self._fname = fname

    def __call__(self, cond, string, **kwargs):
        assert cond, self._fname+": "+string.format(**kwargs)


def assert_X(X, fname=''):
    """
    Checks correctness of the shape of X and raises an assertion if it does not
    conform.
    """
    _assert = Asserter(fname)
    _assert(isinstance(X, np.ndarray),
            "X must be a numpy array. Got type {type}.",
            type=type(X).__name__)

    _assert(X.ndim == 2,
            "X must have 2 dimensions. Got {ndim}.",
            ndim=X.ndim)


def assert_X_multicollinearity(X, fname=''):
    """
    Checks if X has multicollinearity. This will be common if the same
    column is included twice.
    """
    _assert = Asserter(fname)
    if X.shape[1] > 0:
        _assert(np.linalg.cond(np.dot(X.T, X)) < 1e10,
                "Did you include the same column twice? "
                "Perfect multicollinearity detected in X.")


def assert_y(y, fname=''):
    """
    Checks correctness of y and raises an assertion if it does not conform.
    """
    _assert = Asserter(fname)
    _assert(isinstance(y, np.ndarray),
            "y must be a numpy array. Got type {type}.",
            type=type(y).__name__)

    _assert(y.ndim == 1,
            "y must have 1 dimension. Got {ndim}.",
            ndim=y.ndim)


def assert_Xy(X, y, fname=''):
    """
    Checks the correctness of X and y together in context of fitting a model.
    """
    _assert = Asserter(fname)
    assert_X(X, fname=fname)
    assert_y(y, fname=fname)

    _assert(X.shape[0] == y.shape[0],
            "X and y must have the same length along axis 0. "
            "X had length {xlen} and y had length {ylen}.",
            xlen=X.shape[0],
            ylen=y.shape[0])

    assert_X_multicollinearity(X, fname=fname)


def assert_Xbeta(X, beta, fname=''):
    """
    Checks the correctness of X and beta together.
    """
    assert_X(X, fname=fname)

    def _assert(cond, string, **kwargs):
        assert cond, fname+": "+string.format(**kwargs)

    _assert(isinstance(beta, np.ndarray),
            "beta must be a numpy array. Got type {type}.",
            type=type(beta).__name__)

    _assert(beta.ndim == 1,
            "beta must have 1 dimensions. Got {ndim}.",
            ndim=beta.ndim)

    _assert(X.shape[1] + 1 == beta.shape[0],
            "X must have one less column than the length of beta. "
            "X had {xcol} column(s) and beta had length {betalen}.",
            xcol=X.shape[1],
            betalen=beta.shape[0])

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: _dict_learning.py
# MODULE: learning._dict_learning
# DESCRIPTION: Implements dictionary learning algorithms, including online and batch methods.
#              Based on scikit-learn's implementation.
# DEPENDENCIES: numpy, joblib, scipy, scikit-learn (base, linear_model, utils)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ΛORIGIN_AGENT: Jules-04
# ΛTASK_ID: 171-176
# ΛCOMMIT_WINDOW: pre-audit
# ΛAPPROVED_BY: Human Overseer (GRDM)
# ΛUDIT: Standardized header/footer, added comments, normalized logger, applied ΛTAGs.

"""Dictionary learning."""

# Authors: The scikit-learn developers
# SPDX-License-Identifier: BSD-3-Clause

import itertools
import sys
import time
from numbers import Integral, Real

import numpy as np
from joblib import effective_n_jobs
from scipy import linalg

# ΛTRACE: Initialize logger for learning phase
# TAG:consciousness
# TAG:reflection
# TAG:neuroplastic
# TAG:colony
from ..base import (
    BaseEstimator,
    ClassNamePrefixFeaturesOutMixin,
    TransformerMixin,
    _fit_context,
)
from ..linear_model import Lars, Lasso, LassoLars, orthogonal_mp_gram
from ..utils import (
    check_array,
    check_random_state,
    gen_batches,
    gen_even_slices,
)
from ..utils._param_validation import Interval, StrOptions, validate_params
from ..utils.extmath import _randomized_svd, row_norms, svd_flip
from ..utils.parallel import Parallel, delayed
from ..utils.validation import check_is_fitted, validate_data


# # Helper function to check for positive coding constraints
def _check_positive_coding(method, positive):
    # ΛNOTE: Validates if the chosen method supports positive constraints.
    if positive and method in ["omp", "lars"]:
        # ΛTRACE: Logging constraint violation
        logger.error(
            "constraint_violation",
            method=method,
            constraint="positive",
            message="Positive constraint not supported for this coding method.",
        )
        raise ValueError(f"Positive constraint not supported for '{method}' coding method.")


# # Generic sparse coding with precomputed Gram and/or covariance matrices.
def _sparse_encode_precomputed(
    X,
    dictionary,
    *,
    gram=None,
    cov=None,
    algorithm="lasso_lars",
    regularization=None,
    copy_cov=True,
    init=None,
    max_iter=1000,
    verbose=0,
    positive=False,
):
    # ΛNOTE: Core sparse encoding logic using precomputed matrices. This is a performance optimization.
    # ΛTRACE: Starting sparse encoding with precomputed matrices.
    logger.debug(
        "sparse_encode_precomputed_start",
        algorithm=algorithm,
        X_shape=X.shape,
        dict_shape=dictionary.shape,
        positive=positive,
    )
    n_samples, n_features = X.shape
    n_components = dictionary.shape[0]

    if algorithm == "lasso_lars":
        alpha = float(regularization) / n_features  # account for scaling
        try:
            err_mgt = np.seterr(all="ignore")  # ΛCAUTION: Ignoring all numpy errors here. Could mask issues.

            # Not passing in verbose=max(0, verbose-1) because Lars.fit already
            # corrects the verbosity level.
            lasso_lars = LassoLars(
                alpha=alpha,
                fit_intercept=False,
                verbose=verbose,
                precompute=gram,
                fit_path=False,
                positive=positive,
                max_iter=max_iter,
            )
            lasso_lars.fit(dictionary.T, X.T, Xy=cov)
            new_code = lasso_lars.coef_
        finally:
            np.seterr(**err_mgt)

    elif algorithm == "lasso_cd":
        alpha = float(regularization) / n_features  # account for scaling

        clf = Lasso(
            alpha=alpha,
            fit_intercept=False,
            precompute=gram,
            max_iter=max_iter,
            warm_start=True,
            positive=positive,
        )

        if init is not None:  # ΛSEED: Initialization code can be a seed for the learning process.
            if not init.flags["WRITEABLE"]:
                init = np.array(init)
            clf.coef_ = init

        clf.fit(dictionary.T, X.T, check_input=False)
        new_code = clf.coef_

    elif algorithm == "lars":
        try:
            err_mgt = np.seterr(all="ignore")  # ΛCAUTION: Ignoring all numpy errors.

            lars = Lars(
                fit_intercept=False,
                verbose=verbose,
                precompute=gram,
                n_nonzero_coefs=int(regularization),
                fit_path=False,
            )
            lars.fit(dictionary.T, X.T, Xy=cov)
            new_code = lars.coef_
        finally:
            np.seterr(**err_mgt)

    elif algorithm == "threshold":
        new_code = (np.sign(cov) * np.maximum(np.abs(cov) - regularization, 0)).T
        if positive:
            np.clip(new_code, 0, None, out=new_code)

    elif algorithm == "omp":
        new_code = orthogonal_mp_gram(
            Gram=gram,
            Xy=cov,
            n_nonzero_coefs=int(regularization),
            tol=None,
            norms_squared=row_norms(X, squared=True),
            copy_Xy=copy_cov,
        ).T
    # ΛTRACE: Finished sparse encoding with precomputed matrices.
    logger.debug(
        "sparse_encode_precomputed_end",
        algorithm=algorithm,
        code_shape=new_code.reshape(n_samples, n_components).shape,
    )
    return new_code.reshape(n_samples, n_components)


# # Main sparse encoding function
# ΛEXPOSE: This function is likely used by other modules or an API for sparse encoding.
@validate_params(
    {
        "X": ["array-like"],
        "dictionary": ["array-like"],
        "gram": ["array-like", None],
        "cov": ["array-like", None],
        "algorithm": [StrOptions({"lasso_lars", "lasso_cd", "lars", "omp", "threshold"})],
        "n_nonzero_coefs": [Interval(Integral, 1, None, closed="left"), None],
        "alpha": [Interval(Real, 0, None, closed="left"), None],
        "copy_cov": ["boolean"],
        "init": [
            "array-like",
            None,
        ],  # ΛSEED: `init` can act as a seed for the optimization.
        "max_iter": [Interval(Integral, 0, None, closed="left")],
        "n_jobs": [Integral, None],
        "check_input": ["boolean"],
        "verbose": ["verbose"],
        "positive": ["boolean"],
    },
    prefer_skip_nested_validation=True,
)
def sparse_encode(
    X,
    dictionary,
    *,
    gram=None,
    cov=None,
    algorithm="lasso_lars",
    n_nonzero_coefs=None,
    alpha=None,
    copy_cov=True,
    init=None,  # ΛSEED: Initialization for sparse codes can be considered a seed.
    max_iter=1000,
    n_jobs=None,
    check_input=True,
    verbose=0,
    positive=False,
):
    # ΛNOTE: Solves the sparse coding problem X ~= code * dictionary. This is a fundamental operation in dictionary learning.
    # ΛTRACE: Starting sparse encoding.
    logger.info(
        "sparse_encode_start",
        algorithm=algorithm,
        X_shape=X.shape if hasattr(X, "shape") else "unknown",
        dict_shape=dictionary.shape if hasattr(dictionary, "shape") else "unknown",
        positive=positive,
        alpha=alpha,
        n_nonzero_coefs=n_nonzero_coefs,
    )

    if check_input:
        if algorithm == "lasso_cd":
            dictionary = check_array(dictionary, order="C", dtype=[np.float64, np.float32])
            X = check_array(X, order="C", dtype=[np.float64, np.float32])
        else:
            dictionary = check_array(dictionary)
            X = check_array(X)

    if dictionary.shape[1] != X.shape[1]:
        # ΛTRACE: Logging shape mismatch error
        logger.error(
            "shape_mismatch",
            dict_shape=dictionary.shape,
            X_shape=X.shape,
            message="Dictionary and X have different numbers of features.",
        )
        raise ValueError(
            f"Dictionary and X have different numbers of features:dictionary.shape: {dictionary.shape} X.shape{X.shape}"
        )

    _check_positive_coding(algorithm, positive)

    result_code = _sparse_encode(
        X,
        dictionary,
        gram=gram,
        cov=cov,
        algorithm=algorithm,
        n_nonzero_coefs=n_nonzero_coefs,
        alpha=alpha,
        copy_cov=copy_cov,
        init=init,
        max_iter=max_iter,
        n_jobs=n_jobs,
        verbose=verbose,
        positive=positive,
    )
    # ΛTRACE: Finished sparse encoding.
    logger.info("sparse_encode_end", algorithm=algorithm, code_shape=result_code.shape)
    return result_code


# # Internal sparse encoding logic without validation
def _sparse_encode(
    X,
    dictionary,
    *,
    gram=None,
    cov=None,
    algorithm="lasso_lars",
    n_nonzero_coefs=None,
    alpha=None,
    copy_cov=True,
    init=None,  # ΛSEED: Initialization for sparse codes.
    max_iter=1000,
    n_jobs=None,
    verbose=0,
    positive=False,
):
    # ΛNOTE: Internal helper for sparse_encode, handles parallel execution.
    # ΛTRACE: Internal sparse encoding execution.
    logger.debug("_sparse_encode_internal", algorithm=algorithm, n_jobs=n_jobs)
    n_samples, n_features = X.shape
    n_components = dictionary.shape[0]

    if algorithm in ("lars", "omp"):
        regularization = n_nonzero_coefs
        if regularization is None:
            regularization = min(max(n_features / 10, 1), n_components)
    else:
        regularization = alpha
        if regularization is None:
            regularization = 1.0

    if gram is None and algorithm != "threshold":
        gram = np.dot(dictionary, dictionary.T)

    if cov is None and algorithm != "lasso_cd":
        copy_cov = False
        cov = np.dot(dictionary, X.T)

    if effective_n_jobs(n_jobs) == 1 or algorithm == "threshold":
        code = _sparse_encode_precomputed(
            X,
            dictionary,
            gram=gram,
            cov=cov,
            algorithm=algorithm,
            regularization=regularization,
            copy_cov=copy_cov,
            init=init,
            max_iter=max_iter,
            verbose=verbose,
            positive=positive,
        )
        return code

    # Enter parallel code block
    n_samples = X.shape[0]
    n_components = dictionary.shape[0]
    code = np.empty((n_samples, n_components))
    slices = list(gen_even_slices(n_samples, effective_n_jobs(n_jobs)))

    # ΛTRACE: Parallel sparse encoding initiated.
    logger.debug(
        "parallel_sparse_encode_start",
        num_slices=len(slices),
        n_jobs=effective_n_jobs(n_jobs),
    )
    code_views = Parallel(n_jobs=n_jobs, verbose=verbose)(
        delayed(_sparse_encode_precomputed)(
            X[this_slice],
            dictionary,
            gram=gram,
            cov=cov[:, this_slice] if cov is not None else None,
            algorithm=algorithm,
            regularization=regularization,
            copy_cov=copy_cov,
            init=init[this_slice] if init is not None else None,  # ΛSEED: Sliced init.
            max_iter=max_iter,
            verbose=verbose,
            positive=positive,
        )
        for this_slice in slices
    )
    for this_slice, this_view in zip(slices, code_views):
        code[this_slice] = this_view
    # ΛTRACE: Parallel sparse encoding finished.
    logger.debug("parallel_sparse_encode_end")
    return code


# # Updates the dictionary atoms in place
def _update_dict(
    dictionary,
    Y,
    code,
    A=None,
    B=None,
    verbose=False,
    random_state=None,
    positive=False,
):
    # ΛNOTE: This function updates the dictionary atoms. It's a critical step in dictionary learning.
    # ΛDREAM_LOOP: The dictionary update based on the current sparse codes (code) and data (Y) is part of the iterative learning loop.
    # ΛTRACE: Starting dictionary update.
    logger.debug(
        "update_dict_start",
        dict_shape=dictionary.shape,
        Y_shape=Y.shape,
        code_shape=code.shape,
        positive=positive,
    )
    n_samples, n_components = code.shape
    random_state = check_random_state(random_state)

    if A is None:
        A = code.T @ code
    if B is None:
        B = Y.T @ code

    n_unused = 0

    for k in range(n_components):
        if A[k, k] > 1e-6:
            dictionary[k] += (B[:, k] - A[k] @ dictionary) / A[k, k]
        else:
            # ΛNOTE: Atom is unused, resampling it from data. This helps prevent degenerate dictionaries.
            # ΛSEED: Resampling an atom from data (Y) acts as injecting a new seed or
            # refreshing an existing one.
            newd = Y[random_state.choice(n_samples)]
            noise_level = 0.01 * (newd.std() or 1)
            noise = random_state.normal(0, noise_level, size=len(newd))
            dictionary[k] = newd + noise
            code[:, k] = 0  # ΛNOTE: Resetting code for the new atom.
            n_unused += 1
            # ΛTRACE: Resampled unused atom.
            logger.info("resampled_atom", atom_index=k, noise_level=noise_level)

        if positive:
            np.clip(dictionary[k], 0, None, out=dictionary[k])

        dictionary[k] /= max(linalg.norm(dictionary[k]), 1)  # ΛNOTE: Normalizing atom.

    if verbose and n_unused > 0:
        print(f"{n_unused} unused atoms resampled.")
        # ΛTRACE: Reporting number of resampled atoms during dictionary update.
        logger.info("update_dict_resampled_summary", n_unused=n_unused)
    # ΛTRACE: Finished dictionary update.
    logger.debug("update_dict_end")


# # Main dictionary learning algorithm (batch version)
def _dict_learning(
    X,
    n_components,
    *,
    alpha,
    max_iter,
    tol,
    method,
    n_jobs,
    dict_init,  # ΛSEED: Initial dictionary can be a seed.
    code_init,  # ΛSEED: Initial code can be a seed.
    callback,
    verbose,
    random_state,
    return_n_iter,
    positive_dict,
    positive_code,
    method_max_iter,
):
    # ΛNOTE: This is the core batch dictionary learning algorithm. It iteratively updates codes and the dictionary.
    # ΛDREAM_LOOP: The iterative process of updating codes and then the dictionary forms a learning loop.
    # ΛTRACE: Starting batch dictionary learning.
    logger.info(
        "dict_learning_batch_start",
        n_components=n_components,
        alpha=alpha,
        max_iter=max_iter,
        method=method,
    )
    t0 = time.time()
    if code_init is not None and dict_init is not None:
        code = np.array(code_init, order="F")
        dictionary = dict_init
    else:
        # ΛSEED: SVD of data X is used as an initial seed for dictionary and code.
        code, S, dictionary = linalg.svd(X, full_matrices=False)
        code, dictionary = svd_flip(code, dictionary)
        dictionary = S[:, np.newaxis] * dictionary
    r = len(dictionary)
    if n_components <= r:
        code = code[:, :n_components]
        dictionary = dictionary[:n_components, :]
    else:
        code = np.c_[code, np.zeros((len(code), n_components - r))]
        dictionary = np.r_[dictionary, np.zeros((n_components - r, dictionary.shape[1]))]

    dictionary = np.asfortranarray(dictionary)
    errors = []
    current_cost = np.nan
    ii = -1

    for ii in range(max_iter):
        dt = time.time() - t0
        if verbose == 1:
            sys.stdout.write(".")
            sys.stdout.flush()
        elif verbose:
            # ΛTRACE: Logging iteration progress.
            logger.debug(
                "dict_learning_iteration",
                iteration=ii,
                elapsed_time_s=dt,
                current_cost=current_cost,
            )
            print(
                "Iteration % 3i (elapsed time: % 3is, % 4.1fmn, current cost % 7.3f)" % (ii, dt, dt / 60, current_cost)
            )

        # Update code
        code = sparse_encode(
            X,
            dictionary,
            algorithm=method,
            alpha=alpha,
            init=code,  # ΛSEED: Previous code acts as init for next iteration.
            n_jobs=n_jobs,
            positive=positive_code,
            max_iter=method_max_iter,
            verbose=verbose,
        )

        # Update dictionary
        _update_dict(
            dictionary,
            X,
            code,
            verbose=verbose,
            random_state=random_state,
            positive=positive_dict,
        )

        current_cost = 0.5 * np.sum((X - code @ dictionary) ** 2) + alpha * np.sum(np.abs(code))
        errors.append(current_cost)
        # ΛTRACE: Cost calculated for iteration.
        logger.debug("dict_learning_cost", iteration=ii, cost=current_cost)

        if ii > 0:
            dE = errors[-2] - errors[-1]
            if dE < tol * errors[-1]:
                if verbose == 1:
                    print("")
                elif verbose:
                    print("--- Convergence reached after %d iterations" % ii)
                # ΛTRACE: Convergence reached.
                logger.info(
                    "dict_learning_convergence",
                    iteration=ii,
                    reason="dE < tol * errors[-1]",
                )
                break
        if ii % 5 == 0 and callback is not None:
            callback(locals())  # ΛNOTE: Callback for external monitoring or actions.

    # ΛTRACE: Batch dictionary learning finished.
    logger.info(
        "dict_learning_batch_end",
        iterations_completed=ii + 1,
        final_cost=current_cost if errors else np.nan,
    )
    if return_n_iter:
        return code, dictionary, errors, ii + 1
    else:
        return code, dictionary, errors


# # Online dictionary learning
# ΛEXPOSE: This function is likely used by other modules or an API for
# online dictionary learning.
@validate_params(
    {
        "X": ["array-like"],
        "return_code": ["boolean"],
        "method": [StrOptions({"cd", "lars"})],
        "method_max_iter": [Interval(Integral, 0, None, closed="left")],
    },
    prefer_skip_nested_validation=False,
)
def dict_learning_online(
    X,
    n_components=2,
    *,
    alpha=1,
    max_iter=100,
    return_code=True,
    dict_init=None,  # ΛSEED: Initial dictionary.
    callback=None,
    batch_size=256,
    verbose=False,
    shuffle=True,
    n_jobs=None,
    method="lars",
    random_state=None,
    positive_dict=False,
    positive_code=False,
    method_max_iter=1000,
    tol=1e-3,
    max_no_improvement=10,
):
    # ΛNOTE: Solves dictionary learning online using mini-batches. More scalable than batch.
    # ΛDREAM_LOOP: Iterating over mini-batches and updating the dictionary/codes forms a continuous learning loop.
    # ΛTRACE: Starting online dictionary learning.
    logger.info(
        "dict_learning_online_start",
        n_components=n_components,
        alpha=alpha,
        max_iter=max_iter,
        method=method,
        batch_size=batch_size,
    )

    transform_algorithm = "lasso_" + method

    est = MiniBatchDictionaryLearning(
        n_components=n_components,
        alpha=alpha,
        max_iter=max_iter,
        n_jobs=n_jobs,
        fit_algorithm=method,
        batch_size=batch_size,
        shuffle=shuffle,
        dict_init=dict_init,  # ΛSEED: Passed to MiniBatchDictionaryLearning.
        random_state=random_state,
        transform_algorithm=transform_algorithm,
        transform_alpha=alpha,
        positive_code=positive_code,
        positive_dict=positive_dict,
        transform_max_iter=method_max_iter,
        verbose=verbose,
        callback=callback,
        tol=tol,
        max_no_improvement=max_no_improvement,
    ).fit(X)
    # ΛTRACE: Online dictionary learning fitting complete.
    logger.info(
        "dict_learning_online_fit_complete",
        n_iter=est.n_iter_ if hasattr(est, "n_iter_") else "N/A",
    )

    if not return_code:
        return est.components_
    else:
        code = est.transform(X)
        # ΛTRACE: Online dictionary learning transform complete.
        logger.info("dict_learning_online_transform_complete", code_shape=code.shape)
        return code, est.components_


# # Batch dictionary learning (main exposed function)
# ΛEXPOSE: This function is likely used by other modules or an API for
# batch dictionary learning.
@validate_params(
    {
        "X": ["array-like"],
        "method": [StrOptions({"lars", "cd"})],
        "return_n_iter": ["boolean"],
        "method_max_iter": [Interval(Integral, 0, None, closed="left")],
    },
    prefer_skip_nested_validation=False,
)
def dict_learning(
    X,
    n_components,
    *,
    alpha,
    max_iter=100,
    tol=1e-8,
    method="lars",
    n_jobs=None,
    dict_init=None,  # ΛSEED: Initial dictionary.
    code_init=None,  # ΛSEED: Initial code.
    callback=None,
    verbose=False,
    random_state=None,
    return_n_iter=False,
    positive_dict=False,
    positive_code=False,
    method_max_iter=1000,
):
    # ΛNOTE: High-level wrapper for the batch dictionary learning algorithm.
    # ΛTRACE: Preparing for batch dictionary learning via DictionaryLearning class.
    logger.info(
        "dict_learning_wrapper_start",
        n_components=n_components,
        alpha=alpha,
        method=method,
    )
    estimator = DictionaryLearning(
        n_components=n_components,
        alpha=alpha,
        max_iter=max_iter,
        tol=tol,
        fit_algorithm=method,
        n_jobs=n_jobs,
        dict_init=dict_init,  # ΛSEED: Passed to DictionaryLearning.
        callback=callback,
        code_init=code_init,  # ΛSEED: Passed to DictionaryLearning.
        verbose=verbose,
        random_state=random_state,
        positive_code=positive_code,
        positive_dict=positive_dict,
        transform_max_iter=method_max_iter,
    ).set_output(transform="default")
    code = estimator.fit_transform(X)
    # ΛTRACE: Batch dictionary learning via DictionaryLearning class complete.
    logger.info("dict_learning_wrapper_end", n_iter=estimator.n_iter_)

    if return_n_iter:
        return (
            code,
            estimator.components_,
            estimator.error_,
            estimator.n_iter_,
        )
    return code, estimator.components_, estimator.error_


# # Base class for SparseCoder and DictionaryLearning
class _BaseSparseCoding(ClassNamePrefixFeaturesOutMixin, TransformerMixin):
    # ΛNOTE: Base class providing common transform/inverse_transform logic.
    def __init__(
        self,
        transform_algorithm,
        transform_n_nonzero_coefs,
        transform_alpha,
        split_sign,
        n_jobs,
        positive_code,
        transform_max_iter,
    ):
        self.transform_algorithm = transform_algorithm
        self.transform_n_nonzero_coefs = transform_n_nonzero_coefs
        self.transform_alpha = transform_alpha
        self.transform_max_iter = transform_max_iter
        self.split_sign = split_sign
        self.n_jobs = n_jobs
        self.positive_code = positive_code

    # # Private transform method
    def _transform(self, X, dictionary):
        # ΛNOTE: Internal transform logic.
        # ΛTRACE: Base sparse coding transform called.
        logger.debug(
            "_base_sparse_coding_transform",
            transform_algorithm=self.transform_algorithm,
        )
        X = validate_data(self, X, reset=False)  # TODO: original code uses self, but should be X?

        if hasattr(self, "alpha") and self.transform_alpha is None:
            transform_alpha = self.alpha
        else:
            transform_alpha = self.transform_alpha

        code = sparse_encode(
            X,
            dictionary,
            algorithm=self.transform_algorithm,
            n_nonzero_coefs=self.transform_n_nonzero_coefs,
            alpha=transform_alpha,
            max_iter=self.transform_max_iter,
            n_jobs=self.n_jobs,
            positive=self.positive_code,
        )

        if self.split_sign:
            n_samples, n_features = code.shape
            split_code = np.empty((n_samples, 2 * n_features))
            split_code[:, :n_features] = np.maximum(code, 0)
            split_code[:, n_features:] = -np.minimum(code, 0)
            code = split_code
            # ΛTRACE: Code sign split performed.
            logger.debug(
                "code_sign_split_performed",
                original_shape=(n_samples, n_features),
                new_shape=code.shape,
            )

        return code

    # # Public transform method
    # ΛEXPOSE: This method is part of the public API for transforming data.
    def transform(self, X):
        # ΛNOTE: Encodes data as a sparse combination of dictionary atoms.
        check_is_fitted(self)
        # ΛTRACE: Public transform method called.
        logger.info(
            "sparse_coder_transform_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        return self._transform(X, self.components_)

    # # Private inverse transform method
    def _inverse_transform(self, code, dictionary):
        # ΛNOTE: Internal inverse transform logic.
        # ΛTRACE: Base sparse coding inverse_transform called.
        logger.debug("_base_sparse_coding_inverse_transform")
        code = check_array(code)
        expected_n_components = dictionary.shape[0]
        if self.split_sign:
            expected_n_components += expected_n_components
        if code.shape[1] != expected_n_components:
            # ΛTRACE: Logging component mismatch error during inverse transform.
            logger.error(
                "inverse_transform_component_mismatch",
                expected_components=expected_n_components,
                got_components=code.shape[1],
            )
            raise ValueError(
                "The number of components in the code is different from the "
                "number of components in the dictionary."
                f"Expected {expected_n_components}, got {code.shape[1]}."
            )
        if self.split_sign:
            n_samples, n_features = code.shape
            n_features //= 2
            code = code[:, :n_features] - code[:, n_features:]
            # ΛTRACE: Code sign merged for inverse transform.
            logger.debug(
                "code_sign_merged_for_inverse",
                original_shape=(n_samples, n_features * 2),
                new_shape=code.shape,
            )

        return code @ dictionary

    # # Public inverse transform method
    # ΛEXPOSE: This method is part of the public API for reconstructing original data.
    def inverse_transform(self, X):
        # ΛNOTE: Transforms sparse codes back to the original data space.
        check_is_fitted(self)
        # ΛTRACE: Public inverse_transform method called.
        logger.info(
            "sparse_coder_inverse_transform_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        return self._inverse_transform(X, self.components_)


# # SparseCoder class
# ΛEXPOSE: This class is a primary interface for sparse coding.
class SparseCoder(_BaseSparseCoding, BaseEstimator):
    # ΛNOTE: Finds a sparse representation of data against a fixed,
    # precomputed dictionary.
    def __init__(
        self,
        dictionary,  # ΛSEED: The dictionary itself is a seed/basis for encoding.
        *,
        transform_algorithm="omp",
        transform_n_nonzero_coefs=None,
        transform_alpha=None,
        split_sign=False,
        n_jobs=None,
        positive_code=False,
        transform_max_iter=1000,
    ):
        super().__init__(
            transform_algorithm,
            transform_n_nonzero_coefs,
            transform_alpha,
            split_sign,
            n_jobs,
            positive_code,
            transform_max_iter,
        )
        self.dictionary = dictionary
        # ΛTRACE: SparseCoder initialized.
        logger.debug(
            "SparseCoder_initialized",
            transform_algorithm=transform_algorithm,
            dictionary_shape=(dictionary.shape if hasattr(dictionary, "shape") else "unknown"),
        )

    # # Fit method (no-op for SparseCoder)
    def fit(self, X, y=None):
        # ΛNOTE: Fit is a no-op as the dictionary is precomputed and fixed.
        # ΛTRACE: SparseCoder fit called (no-op).
        logger.debug("SparseCoder_fit_called_noop")
        return self

    # # Transform method specific to SparseCoder
    # ΛEXPOSE: Main method to get sparse codes using the fixed dictionary.
    def transform(self, X, y=None):
        # ΛTRACE: SparseCoder specific transform called.
        logger.info(
            "SparseCoder_transform_specific_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        return super()._transform(X, self.dictionary)

    # # Inverse transform method specific to SparseCoder
    # ΛEXPOSE: Main method to reconstruct data from sparse codes.
    def inverse_transform(self, X):
        # ΛTRACE: SparseCoder specific inverse_transform called.
        logger.info(
            "SparseCoder_inverse_transform_specific_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        return self._inverse_transform(X, self.dictionary)

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags["requires_fit"] = False
        tags["transformer_tags.preserves_dtype"] = ["float64", "float32"]
        return tags

    @property
    def n_components_(self):
        return self.dictionary.shape[0]

    @property
    def n_features_in_(self):
        return self.dictionary.shape[1]

    @property
    def _n_features_out(self):
        return self.n_components_


# # DictionaryLearning class
# ΛEXPOSE: This class is a primary interface for learning dictionaries.
class DictionaryLearning(_BaseSparseCoding, BaseEstimator):
    # ΛNOTE: Learns a dictionary (set of atoms) that sparsely encodes the data.
    _parameter_constraints: dict = {
        "n_components": [Interval(Integral, 1, None, closed="left"), None],
        "alpha": [Interval(Real, 0, None, closed="left")],
        "max_iter": [Interval(Integral, 0, None, closed="left")],
        "tol": [Interval(Real, 0, None, closed="left")],
        "fit_algorithm": [StrOptions({"lars", "cd"})],
        "transform_algorithm": [StrOptions({"lasso_lars", "lasso_cd", "lars", "omp", "threshold"})],
        "transform_n_nonzero_coefs": [Interval(Integral, 1, None, closed="left"), None],
        "transform_alpha": [Interval(Real, 0, None, closed="left"), None],
        "n_jobs": [Integral, None],
        "code_init": [np.ndarray, None],  # ΛSEED: Initial code can be a seed.
        "dict_init": [np.ndarray, None],  # ΛSEED: Initial dictionary can be a seed.
        "callback": [callable, None],
        "verbose": ["verbose"],
        "split_sign": ["boolean"],
        "random_state": ["random_state"],
        "positive_code": ["boolean"],
        "positive_dict": ["boolean"],
        "transform_max_iter": [Interval(Integral, 0, None, closed="left")],
    }

    def __init__(
        self,
        n_components=None,
        *,
        alpha=1,
        max_iter=1000,
        tol=1e-8,
        fit_algorithm="lars",
        transform_algorithm="omp",
        transform_n_nonzero_coefs=None,
        transform_alpha=None,
        n_jobs=None,
        code_init=None,  # ΛSEED: Initial code.
        dict_init=None,  # ΛSEED: Initial dictionary.
        callback=None,
        verbose=False,
        split_sign=False,
        random_state=None,
        positive_code=False,
        positive_dict=False,
        transform_max_iter=1000,
    ):
        super().__init__(
            transform_algorithm,
            transform_n_nonzero_coefs,
            transform_alpha,
            split_sign,
            n_jobs,
            positive_code,
            transform_max_iter,
        )
        self.n_components = n_components
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.fit_algorithm = fit_algorithm
        self.code_init = code_init
        self.dict_init = dict_init
        self.callback = callback
        self.verbose = verbose
        self.random_state = random_state
        self.positive_dict = positive_dict
        # ΛTRACE: DictionaryLearning initialized.
        logger.debug(
            "DictionaryLearning_initialized",
            n_components=n_components,
            alpha=alpha,
            fit_algorithm=fit_algorithm,
        )

    # # Fit method
    # ΛEXPOSE: Main method to learn the dictionary from data.
    def fit(self, X, y=None):
        # ΛDREAM_LOOP: The fit process involves iteratively refining the dictionary, which is a learning loop.
        # ΛTRACE: DictionaryLearning fit called.
        logger.info(
            "DictionaryLearning_fit_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        self.fit_transform(X)
        return self

    # # Fit and transform method
    # ΛEXPOSE: Learns dictionary and returns sparse codes.
    @_fit_context(prefer_skip_nested_validation=True)
    def fit_transform(self, X, y=None):
        # ΛDREAM_LOOP: Core learning loop is invoked here.
        _check_positive_coding(method=self.fit_algorithm, positive=self.positive_code)
        method = "lasso_" + self.fit_algorithm
        random_state = check_random_state(self.random_state)
        X = validate_data(self, X)

        n_components = X.shape[1] if self.n_components is None else self.n_components
        # ΛTRACE: DictionaryLearning fit_transform starting internal _dict_learning.
        logger.info(
            "DictionaryLearning_fit_transform_start_internal",
            n_components=n_components,
            method=method,
        )

        V, U, E, self.n_iter_ = _dict_learning(
            X,
            n_components,
            alpha=self.alpha,
            tol=self.tol,
            max_iter=self.max_iter,
            method=method,
            method_max_iter=self.transform_max_iter,
            n_jobs=self.n_jobs,
            code_init=self.code_init,  # ΛSEED: Passed to internal learner.
            dict_init=self.dict_init,  # ΛSEED: Passed to internal learner.
            callback=self.callback,
            verbose=self.verbose,
            random_state=random_state,
            return_n_iter=True,
            positive_dict=self.positive_dict,
            positive_code=self.positive_code,
        )
        self.components_ = U  # This is the learned dictionary
        self.error_ = E
        # ΛTRACE: DictionaryLearning fit_transform completed internal _dict_learning.
        logger.info(
            "DictionaryLearning_fit_transform_end_internal",
            n_iter=self.n_iter_,
            final_error=E[-1] if E else "N/A",
        )

        return V  # This is the sparse code

    @property
    def _n_features_out(self):
        return self.components_.shape[0]

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags["transformer_tags.preserves_dtype"] = ["float64", "float32"]
        return tags


# # MiniBatchDictionaryLearning class
# ΛEXPOSE: This class provides a more scalable way to learn dictionaries
# using mini-batches.
class MiniBatchDictionaryLearning(_BaseSparseCoding, BaseEstimator):
    # ΛNOTE: Finds a dictionary using mini-batch optimization. Faster for
    # large datasets.
    _parameter_constraints: dict = {
        "n_components": [Interval(Integral, 1, None, closed="left"), None],
        "alpha": [Interval(Real, 0, None, closed="left")],
        "max_iter": [Interval(Integral, 0, None, closed="left")],
        "fit_algorithm": [StrOptions({"cd", "lars"})],
        "n_jobs": [None, Integral],
        "batch_size": [Interval(Integral, 1, None, closed="left")],
        "shuffle": ["boolean"],
        "dict_init": [None, np.ndarray],  # ΛSEED: Initial dictionary.
        "transform_algorithm": [StrOptions({"lasso_lars", "lasso_cd", "lars", "omp", "threshold"})],
        "transform_n_nonzero_coefs": [Interval(Integral, 1, None, closed="left"), None],
        "transform_alpha": [Interval(Real, 0, None, closed="left"), None],
        "verbose": ["verbose"],
        "split_sign": ["boolean"],
        "random_state": ["random_state"],
        "positive_code": ["boolean"],
        "positive_dict": ["boolean"],
        "transform_max_iter": [Interval(Integral, 0, None, closed="left")],
        "callback": [None, callable],
        "tol": [Interval(Real, 0, None, closed="left")],
        "max_no_improvement": [Interval(Integral, 0, None, closed="left"), None],
    }

    def __init__(
        self,
        n_components=None,
        *,
        alpha=1,
        max_iter=1_000,
        fit_algorithm="lars",
        n_jobs=None,
        batch_size=256,
        shuffle=True,
        dict_init=None,  # ΛSEED: Initial dictionary.
        transform_algorithm="omp",
        transform_n_nonzero_coefs=None,
        transform_alpha=None,
        verbose=False,
        split_sign=False,
        random_state=None,
        positive_code=False,
        positive_dict=False,
        transform_max_iter=1000,
        callback=None,
        tol=1e-3,
        max_no_improvement=10,
    ):
        super().__init__(
            transform_algorithm,
            transform_n_nonzero_coefs,
            transform_alpha,
            split_sign,
            n_jobs,
            positive_code,
            transform_max_iter,
        )
        self.n_components = n_components
        self.alpha = alpha
        self.max_iter = max_iter
        self.fit_algorithm = fit_algorithm
        self.dict_init = dict_init
        self.verbose = verbose
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.split_sign = split_sign
        self.random_state = random_state
        self.positive_dict = positive_dict
        self.callback = callback
        self.max_no_improvement = max_no_improvement
        self.tol = tol
        # ΛTRACE: MiniBatchDictionaryLearning initialized.
        logger.debug(
            "MiniBatchDictionaryLearning_initialized",
            n_components=n_components,
            alpha=alpha,
            batch_size=batch_size,
        )

    # # Check parameters internal method
    def _check_params(self, X):
        self._n_components = self.n_components
        if self._n_components is None:
            self._n_components = X.shape[1]
        _check_positive_coding(self.fit_algorithm, self.positive_code)
        self._fit_algorithm = "lasso_" + self.fit_algorithm
        self._batch_size = min(self.batch_size, X.shape[0])
        # ΛTRACE: Parameters checked for MiniBatchDictionaryLearning.
        logger.debug(
            "_check_params_complete",
            n_components=self._n_components,
            fit_algorithm=self._fit_algorithm,
            batch_size=self._batch_size,
        )

    # # Initialize dictionary internal method
    def _initialize_dict(self, X, random_state):
        # ΛNOTE: Initializes dictionary, using SVD if no `dict_init` is provided.
        # ΛSEED: `dict_init` or SVD output acts as initial seed for the dictionary.
        if self.dict_init is not None:
            dictionary = self.dict_init
            # ΛTRACE: Dictionary initialized from dict_init.
            logger.info("dictionary_initialized_from_dict_init", dict_shape=dictionary.shape)
        else:
            _, S, dictionary = _randomized_svd(X, self._n_components, random_state=random_state)
            dictionary = S[:, np.newaxis] * dictionary
            # ΛTRACE: Dictionary initialized using randomized SVD.
            logger.info("dictionary_initialized_from_svd", dict_shape=dictionary.shape)

        if self._n_components <= len(dictionary):
            dictionary = dictionary[: self._n_components, :]
        else:
            dictionary = np.concatenate(
                (
                    dictionary,
                    np.zeros(
                        (self._n_components - len(dictionary), dictionary.shape[1]),
                        dtype=dictionary.dtype,
                    ),
                )
            )
        dictionary = check_array(dictionary, order="F", dtype=X.dtype, copy=False)
        dictionary = np.require(dictionary, requirements="W")
        return dictionary

    # # Update inner statistics for online learning
    def _update_inner_stats(self, X, code, batch_size, step):
        # ΛNOTE: Updates A and B matrices (sufficient statistics) for online updates.
        # ΛDREAM_LOOP: This incremental update of statistics is part of the
        # ongoing learning process.
        if step < batch_size - 1:
            theta = (step + 1) * batch_size
        else:
            theta = batch_size**2 + step + 1 - batch_size
        beta = (theta + 1 - batch_size) / (theta + 1)

        self._A *= beta
        self._A += code.T @ code / batch_size
        self._B *= beta
        self._B += X.T @ code / batch_size
        # ΛTRACE: Inner stats A and B updated.
        logger.debug("inner_stats_updated", step=step, theta=theta, beta=beta)

    # # Perform one mini-batch step
    def _minibatch_step(self, X, dictionary, random_state, step):
        # ΛNOTE: Processes one mini-batch: sparse code, update stats, update dictionary.
        # ΛDREAM_LOOP: Each mini-batch step contributes to the overall learning loop.
        batch_size = X.shape[0]
        # ΛTRACE: Mini-batch step started.
        logger.debug("minibatch_step_start", step=step, batch_size=batch_size)

        code = _sparse_encode(
            X,
            dictionary,
            algorithm=self._fit_algorithm,
            alpha=self.alpha,
            n_jobs=self.n_jobs,
            positive=self.positive_code,
            max_iter=self.transform_max_iter,
            verbose=self.verbose,
        )
        batch_cost = (0.5 * ((X - code @ dictionary) ** 2).sum() + self.alpha * np.sum(np.abs(code))) / batch_size
        # ΛTRACE: Sparse code computed for mini-batch.
        logger.debug("minibatch_sparse_code_computed", step=step, batch_cost=batch_cost)

        self._update_inner_stats(X, code, batch_size, step)
        _update_dict(
            dictionary,
            X,
            # This should be X_batch, but original code uses X. Assuming X is X_batch
            # here.
            code,
            self._A,
            self._B,
            verbose=self.verbose,
            random_state=random_state,
            positive=self.positive_dict,
        )
        # ΛTRACE: Dictionary updated for mini-batch.
        logger.debug("minibatch_dictionary_updated", step=step)
        return batch_cost

    # # Check convergence criteria
    def _check_convergence(self, X, batch_cost, new_dict, old_dict, n_samples, step, n_steps):
        # ΛNOTE: Implements early stopping logic based on dictionary change and
        # cost improvement.
        batch_size = X.shape[0]
        step = step + 1  # User-friendly step count

        if step <= min(100, n_samples / batch_size):
            if self.verbose:
                print(f"Minibatch step {step}/{n_steps}: mean batch cost: {batch_cost}")
            # ΛTRACE: Initial steps, convergence check skipped.
            logger.debug(
                "convergence_check_skipped_initial_steps",
                step=step,
                batch_cost=batch_cost,
            )
            return False

        if self._ewa_cost is None:
            self._ewa_cost = batch_cost
        else:
            alpha_ewa = batch_size / (n_samples + 1)  # Renamed alpha to alpha_ewa to avoid conflict
            alpha_ewa = min(alpha_ewa, 1)
            self._ewa_cost = self._ewa_cost * (1 - alpha_ewa) + batch_cost * alpha_ewa
        # ΛTRACE: EWA cost updated.
        logger.debug(
            "ewa_cost_updated",
            step=step,
            ewa_cost=self._ewa_cost,
            batch_cost=batch_cost,
        )

        if self.verbose:
            print(f"Minibatch step {step}/{n_steps}: mean batch cost: {batch_cost}, ewa cost: {self._ewa_cost}")

        dict_diff = linalg.norm(new_dict - old_dict) / self._n_components
        if self.tol > 0 and dict_diff <= self.tol:
            if self.verbose:
                print(f"Converged (small dictionary change) at step {step}/{n_steps}")
            # ΛTRACE: Convergence due to small dictionary change.
            logger.info(
                "convergence_small_dict_change",
                step=step,
                dict_diff=dict_diff,
                tol=self.tol,
            )
            return True

        if self._ewa_cost_min is None or self._ewa_cost < self._ewa_cost_min:
            self._no_improvement = 0
            self._ewa_cost_min = self._ewa_cost
        else:
            self._no_improvement += 1
        # ΛTRACE: Improvement stats updated.
        logger.debug(
            "improvement_stats_updated",
            step=step,
            no_improvement_count=self._no_improvement,
            ewa_cost_min=self._ewa_cost_min,
        )

        if self.max_no_improvement is not None and self._no_improvement >= self.max_no_improvement:
            if self.verbose:
                print(f"Converged (lack of improvement in objective function) at step {step}/{n_steps}")
            # ΛTRACE: Convergence due to lack of improvement.
            logger.info(
                "convergence_no_improvement",
                step=step,
                no_improvement_count=self._no_improvement,
            )
            return True
        return False

    # # Fit method for MiniBatchDictionaryLearning
    # ΛEXPOSE: Main method to learn the dictionary using mini-batches.
    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        # ΛDREAM_LOOP: The fit process iteratively processes mini-batches, forming a learning loop.
        # ΛTRACE: MiniBatchDictionaryLearning fit called.
        logger.info(
            "MiniBatchDictionaryLearning_fit_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        X = validate_data(self, X, dtype=[np.float64, np.float32], order="C", copy=False)
        self._check_params(X)
        self._random_state = check_random_state(self.random_state)
        dictionary = self._initialize_dict(X, self._random_state)
        old_dict = dictionary.copy()

        if self.shuffle:
            X_train = X.copy()
            self._random_state.shuffle(X_train)
        else:
            X_train = X
        n_samples, n_features = X_train.shape

        if self.verbose:
            print("[dict_learning]")
        self._A = np.zeros((self._n_components, self._n_components), dtype=X_train.dtype)
        self._B = np.zeros((n_features, self._n_components), dtype=X_train.dtype)
        self._ewa_cost = None
        self._ewa_cost_min = None
        self._no_improvement = 0

        batches = gen_batches(n_samples, self._batch_size)
        batches = itertools.cycle(batches)
        n_steps_per_iter = int(np.ceil(n_samples / self._batch_size))
        n_steps = self.max_iter * n_steps_per_iter
        i = -1

        for i, batch_slice in zip(range(n_steps), batches):  # Renamed batch to batch_slice
            X_batch = X_train[batch_slice]
            batch_cost = self._minibatch_step(X_batch, dictionary, self._random_state, i)
            if self._check_convergence(X_batch, batch_cost, dictionary, old_dict, n_samples, i, n_steps):
                break
            if self.callback is not None:
                self.callback(locals())
            old_dict[:] = dictionary

        self.n_steps_ = i + 1
        self.n_iter_ = np.ceil(self.n_steps_ / n_steps_per_iter)
        self.components_ = dictionary
        # ΛTRACE: MiniBatchDictionaryLearning fit completed.
        logger.info(
            "MiniBatchDictionaryLearning_fit_completed",
            n_steps=self.n_steps_,
            n_iter=self.n_iter_,
        )
        return self

    # # Partial fit method for online learning
    # ΛEXPOSE: Allows for incremental learning from new mini-batches.
    @_fit_context(prefer_skip_nested_validation=True)
    def partial_fit(self, X, y=None):
        # ΛDREAM_LOOP: Each call to partial_fit is a step in an ongoing learning loop.
        # ΛTRACE: MiniBatchDictionaryLearning partial_fit called.
        logger.info(
            "MiniBatchDictionaryLearning_partial_fit_called",
            X_shape=X.shape if hasattr(X, "shape") else "unknown",
        )
        has_components = hasattr(self, "components_")
        X = validate_data(self, X, dtype=[np.float64, np.float32], order="C", reset=not has_components)

        if not has_components:
            self._check_params(X)
            self._random_state = check_random_state(self.random_state)
            dictionary = self._initialize_dict(X, self._random_state)
            self.n_steps_ = 0
            self._A = np.zeros((self._n_components, self._n_components), dtype=X.dtype)
            self._B = np.zeros((X.shape[1], self._n_components), dtype=X.dtype)
            # ΛTRACE: Initializing for first partial_fit.
            logger.info("partial_fit_initialization")
        else:
            dictionary = self.components_

        self._minibatch_step(X, dictionary, self._random_state, self.n_steps_)
        self.components_ = dictionary
        self.n_steps_ += 1
        # ΛTRACE: MiniBatchDictionaryLearning partial_fit step completed.
        logger.info("partial_fit_step_completed", current_n_steps=self.n_steps_)
        return self

    @property
    def _n_features_out(self):
        return self.components_.shape[0]

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags["transformer_tags.preserves_dtype"] = ["float64", "float32"]
        return tags


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: _dict_learning.py
# VERSION: 1.1 (Jules-04 update)
# TIER SYSTEM: N/A (Core algorithm)
# ΛTRACE INTEGRATION: ENABLED (structlog)
# CAPABILITIES: Batch dictionary learning, Online dictionary learning, Sparse coding
# FUNCTIONS: _check_positive_coding, _sparse_encode_precomputed, sparse_encode,
#            _sparse_encode, _update_dict, _dict_learning, dict_learning_online,
#            dict_learning
# CLASSES: _BaseSparseCoding, SparseCoder, DictionaryLearning, MiniBatchDictionaryLearning
# DECORATORS: @validate_params, @property, @_fit_context
# DEPENDENCIES: numpy, joblib, scipy, scikit-learn (base, linear_model, utils), structlog
# INTERFACES: Standard scikit-learn Estimator/Transformer API (fit, transform, fit_transform, inverse_transform)
# ERROR HANDLING: ValueError for invalid parameters or constraints. Numpy errors potentially masked in some lars/lasso_lars sections.
# LOGGING: ΛTRACE_ENABLED via structlog, bound with tag="learning_phase"
# AUTHENTICATION: N/A
# HOW TO USE:
#   Use `DictionaryLearning` or `MiniBatchDictionaryLearning` to learn a dictionary from data.
#   Use `SparseCoder` to encode data using a pre-existing dictionary.
#   Use `sparse_encode` for direct sparse coding functionality.
#   Example:
#     from sklearn.decomposition import DictionaryLearning
#     learner = DictionaryLearning(n_components=10, alpha=0.1)
#     codes = learner.fit_transform(data_matrix)
#     dictionary = learner.components_
# INTEGRATION NOTES: Core component for feature learning and sparse representations.
#                    Integrates with other scikit-learn modules.
# MAINTENANCE: Align with scikit-learn updates if base code changes. Monitor error masking.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

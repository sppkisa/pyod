# -*- coding: utf-8 -*-
"""Outlier Detection with Minimum Covariance Determinant (MCD)
"""
# Author: Yue Zhao <zhaoy@cmu.edu>
# License: BSD 2 clause

from __future__ import division
from __future__ import print_function

from sklearn.covariance import MinCovDet
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.validation import check_array

from .base import BaseDetector

__all__ = ['MCD']


class MCD(BaseDetector):
    """Detecting outliers in a Gaussian distributed dataset using
    Minimum Covariance Determinant (MCD): robust estimator of covariance.

    The Minimum Covariance Determinant covariance estimator is to be applied
    on Gaussian-distributed data, but could still be relevant on data
    drawn from a unimodal, symmetric distribution. It is not meant to be used
    with multi-modal data (the algorithm used to fit a MinCovDet object is
    likely to fail in such a case).
    One should consider projection pursuit methods to deal with multi-modal
    datasets.

    First fit a minimum covariance determinant model and then compute the
    Mahalanobis distance as the outlier degree of the data

    See :cite:`rousseeuw1999fast,hardin2004outlier` for details.

    Parameters
    ----------
    contamination : float in (0., 0.5), optional (default=0.1)
        The amount of contamination of the data set,
        i.e. the proportion of outliers in the data set. Used when fitting to
        define the threshold on the decision function.

    store_precision : bool
        Specify if the estimated precision is stored.

    assume_centered : Boolean
        If True, the support of the robust location and the covariance
        estimates is computed, and a covariance estimate is recomputed from
        it, without centering the data.
        Useful to work with data whose mean is significantly equal to
        zero but is not exactly zero.
        If False, the robust location and covariance are directly computed
        with the FastMCD algorithm without additional treatment.

    support_fraction : float, 0 < support_fraction < 1
        The proportion of points to be included in the support of the raw
        MCD estimate. Default is None, which implies that the minimum
        value of support_fraction will be used within the algorithm:
        [n_sample + n_features + 1] / 2

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Attributes
    ----------
    raw_location_ : array-like, shape (n_features,)
        The raw robust estimated location before correction and re-weighting.

    raw_covariance_ : array-like, shape (n_features, n_features)
        The raw robust estimated covariance before correction and re-weighting.

    raw_support_ : array-like, shape (n_samples,)
        A mask of the observations that have been used to compute
        the raw robust estimates of location and shape, before correction
        and re-weighting.

    location_ : array-like, shape (n_features,)
        Estimated robust location

    covariance_ : array-like, shape (n_features, n_features)
        Estimated robust covariance matrix

    precision_ : array-like, shape (n_features, n_features)
        Estimated pseudo inverse matrix.
        (stored only if store_precision is True)

    support_ : array-like, shape (n_samples,)
        A mask of the observations that have been used to compute
        the robust estimates of location and shape.

    decision_scores_ : numpy array of shape (n_samples,)
        The outlier scores of the training data.
        The higher, the more abnormal. Outliers tend to have higher
        scores. This value is available once the detector is
        fitted. Mahalanobis distances of the training set (on which
        `:meth:`fit` is called) observations.

    threshold_ : float
        The threshold is based on ``contamination``. It is the
        ``n_samples * contamination`` most abnormal samples in
        ``decision_scores_``. The threshold is calculated for generating
        binary outlier labels.

    labels_ : int, either 0 or 1
        The binary labels of the training data. 0 stands for inliers
        and 1 for outliers/anomalies. It is generated by applying
        ``threshold_`` on ``decision_scores_``.
    """

    def __init__(self, contamination=0.1, store_precision=True,
                 assume_centered=False, support_fraction=None,
                 random_state=None):
        super(MCD, self).__init__(contamination=contamination)
        self.store_precision = store_precision
        self.assume_centered = assume_centered
        self.support_fraction = support_fraction
        self.random_state = random_state

    # noinspection PyIncorrectDocstring
    def fit(self, X, y=None):
        """Fit detector. y is optional for unsupervised methods.

        Parameters
        ----------
        X : numpy array of shape (n_samples, n_features)
            The input samples.

        y : numpy array of shape (n_samples,), optional (default=None)
            The ground truth of the input samples (labels).
        """
        # Validate inputs X and y (optional)
        X = check_array(X)
        self._set_n_classes(y)

        self.detector_ = MinCovDet(store_precision=self.store_precision,
                                   assume_centered=self.assume_centered,
                                   support_fraction=self.support_fraction,
                                   random_state=self.random_state)
        self.detector_.fit(X=X, y=y)

        # Use mahalanabis distance as the outlier score
        self.decision_scores_ = self.detector_.dist_
        self._process_decision_scores()
        return self

    def decision_function(self, X):
        """Predict raw anomaly score of X using the fitted detector.

        The anomaly score of an input sample is computed based on different
        detector algorithms. For consistency, outliers are assigned with
        larger anomaly scores.

        Parameters
        ----------
        X : numpy array of shape (n_samples, n_features)
            The training input samples. Sparse matrices are accepted only
            if they are supported by the base estimator.

        Returns
        -------
        anomaly_scores : numpy array of shape (n_samples,)
            The anomaly score of the input samples.
        """
        check_is_fitted(self, ['decision_scores_', 'threshold_', 'labels_'])
        X = check_array(X)

        # Computer mahalanobis distance of the samples
        return self.detector_.mahalanobis(X)

    @property
    def raw_location_(self):
        """The raw robust estimated location before correction and
        re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_location_

    @property
    def raw_covariance_(self):
        """The raw robust estimated location before correction and
        re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_covariance_

    @property
    def raw_support_(self):
        """A mask of the observations that have been used to compute
        the raw robust estimates of location and shape, before correction
        and re-weighting.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.raw_support_

    @property
    def location_(self):
        """Estimated robust location.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.location_

    @property
    def covariance_(self):
        """Estimated robust covariance matrix.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.covariance_

    @property
    def precision_(self):
        """ Estimated pseudo inverse matrix.
        (stored only if store_precision is True)

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.precision_

    @property
    def support_(self):
        """A mask of the observations that have been used to compute
        the robust estimates of location and shape.

        Decorator for scikit-learn MinCovDet attributes.
        """
        return self.detector_.support_

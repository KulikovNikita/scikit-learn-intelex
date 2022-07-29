#!/usr/bin/env python
#===============================================================================
# Copyright 2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

# TODO:
# will be replaced
# from daal4py.sklearn.ensemble import RandomForestClassifier
from daal4py.sklearn.ensemble import RandomForestRegressor
# from onedal.ensemble import RandomForestClassifier

from sklearn import __version__ as sklearn_version
import numpy as np

from abc import ABC

from .._device_offload import dispatch, wrap_output_data

from sklearn.ensemble import RandomForestClassifier as sklearn_RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor as sklearn_RandomForestRegressor

from sklearn.utils.validation import _deprecate_positional_args

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree._tree import Tree

from onedal.ensemble import RandomForestClassifier as onedal_RandomForestClassifier
from onedal.ensemble import RandomForestRegressor as onedal_RandomForestRegressor


class BaseRandomForest(ABC):
    def _fit_proba(self, X, y, sample_weight=None, queue=None):
        from .._config import get_config, config_context

        params = self.get_params()
        clf_base = self.__class__(**params)

        # We use stock metaestimators below, so the only way
        # to pass a queue is using config_context.
        cfg = get_config()
        cfg['target_offload'] = queue

    def _save_attributes(self):
        # TODO:
        self.n_features_in_ = self._onedal_estimator.n_features_in_
        self.classes_ = self._onedal_estimator.classes_
        self.n_classes_ = self._onedal_estimator.n_classes_
        self.n_outputs_ = self._onedal_estimator.n_outputs_


class RandomForestClassifier(sklearn_RandomForestClassifier, BaseRandomForest):
    __doc__ = sklearn_RandomForestClassifier.__doc__

    @_deprecate_positional_args
    def __init__(self,
                 n_estimators=100,
                 criterion="gini", *,
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 min_weight_fraction_leaf=0.,
                 max_features="auto",
                 max_leaf_nodes=None,
                 min_impurity_decrease=0.,
                 bootstrap=True,
                 oob_score=False,
                 n_jobs=None,
                 random_state=None,
                 verbose=0,
                 warm_start=False,
                 class_weight=None,
                 ccp_alpha=0.0,
                 max_samples=None,
                 maxBins=256,
                 minBinSize=1):
        super().__init__(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_decrease=min_impurity_decrease,
            bootstrap=bootstrap,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            warm_start=warm_start,
            class_weight=class_weight
        )
        # TODO:
        # update __init__ for different versions sklearn
        self.ccp_alpha = ccp_alpha
        self.max_samples = max_samples
        self.maxBins = maxBins
        self.minBinSize = minBinSize
        self.min_impurity_split = None


    def fit(self, X, y, sample_weight=None):
        """
        Build a forest of trees from the training set (X, y).

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The training input samples. Internally, its dtype will be converted
            to ``dtype=np.float32``. If a sparse matrix is provided, it will be
            converted into a sparse ``csc_matrix``.

        y : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The target values (class labels in classification, real numbers in
            regression).

        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights. If None, then samples are equally weighted. Splits
            that would create child nodes with net zero or negative weight are
            ignored while searching for a split in each node. In the case of
            classification, splits are also ignored if they would result in any
            single class carrying a negative weight in either child node.

        Returns
        -------
        self : object
        """
        dispatch(self, 'ensemble.RandomForestClassifier.fit', {
            'onedal': self.__class__._onedal_fit,
            'sklearn': sklearn_RandomForestClassifier.fit,
        }, X, y, sample_weight)
        self.estimators_ = self._estimators_
        # Decapsulate classes_ attributes
        self.n_classes_ = self.n_classes_[0]
        self.classes_ = self.classes_[0]
        return self


    def predict(self, X):
        """
        Predict class for X.

        The predicted class of an input sample is a vote by the trees in
        the forest, weighted by their probability estimates. That is,
        the predicted class is the one with highest mean probability
        estimate across the trees.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The input samples. Internally, its dtype will be converted to
            ``dtype=np.float32``. If a sparse matrix is provided, it will be
            converted into a sparse ``csr_matrix``.

        Returns
        -------
        y : ndarray of shape (n_samples,) or (n_samples, n_outputs)
            The predicted classes.
        """
        return dispatch(self, 'ensemble.RandomForestClassifier.predict', {
            'onedal': self.__class__._onedal_predict,
            'sklearn': sklearn_RandomForestClassifier.predict,
        }, X)


    def predict_proba(self, X):
        """
        Predict class probabilities for X.

        The predicted class probabilities of an input sample are computed as
        the mean predicted class probabilities of the trees in the forest.
        The class probability of a single tree is the fraction of samples of
        the same class in a leaf.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The input samples. Internally, its dtype will be converted to
            ``dtype=np.float32``. If a sparse matrix is provided, it will be
            converted into a sparse ``csr_matrix``.

        Returns
        -------
        p : ndarray of shape (n_samples, n_classes), or a list of n_outputs
            such arrays if n_outputs > 1.
            The class probabilities of the input samples. The order of the
            classes corresponds to that in the attribute :term:`classes_`.
        """
        self._check_proba()
        return self._predict_proba

    def _estimators_(self):
        if hasattr(self, '_cached_estimators_'):
            if self._cached_estimators_:
                return self._cached_estimators_

        # if sklearn_check_version('0.22'):
        #     check_is_fitted(self)
        # else:
        #     check_is_fitted(self, 'daal_model_')
        classes_ = self.classes_[0]
        n_classes_ = self.n_classes_[0]
        # convert model to estimators
        params = {
            'criterion': self.criterion,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf': self.min_weight_fraction_leaf,
            'max_features': self.max_features,
            'max_leaf_nodes': self.max_leaf_nodes,
            'min_impurity_decrease': self.min_impurity_decrease,
            'random_state': None,
        }
        # if not sklearn_check_version('1.0'):
        #     params['min_impurity_split'] = self.min_impurity_split
        est = DecisionTreeClassifier(**params)
        # TODO:
        # we need to set est.tree_ field with Trees constructed from Intel(R)
        # oneAPI Data Analytics Library solution
        estimators_ = []
#        random_state_checked = check_random_state(self.random_state)
#        for i in range(self.n_estimators):
#            est_i = clone(est)
#            est_i.set_params(
#                random_state=random_state_checked.randint(np.iinfo(np.int32).max))
#            if sklearn_check_version('1.0'):
#                est_i.n_features_in_ = self.n_features_in_
#            else:
#                est_i.n_features_ = self.n_features_in_
#            est_i.n_outputs_ = self.n_outputs_
#            est_i.classes_ = classes_
#            est_i.n_classes_ = n_classes_
#            # treeState members: 'class_count', 'leaf_count', 'max_depth',
#            # 'node_ar', 'node_count', 'value_ar'
#            tree_i_state_class = daal4py.getTreeState(
#                self.daal_model_, i, n_classes_)
#
#            # node_ndarray = tree_i_state_class.node_ar
#            # value_ndarray = tree_i_state_class.value_ar
#            # value_shape = (node_ndarray.shape[0], self.n_outputs_,
#            #                n_classes_)
#            # assert np.allclose(
#            #     value_ndarray, value_ndarray.astype(np.intc, casting='unsafe')
#            # ), "Value array is non-integer"
#            tree_i_state_dict = {
#                'max_depth': tree_i_state_class.max_depth,
#                'node_count': tree_i_state_class.node_count,
#                'nodes': tree_i_state_class.node_ar,
#                'values': tree_i_state_class.value_ar}
#            est_i.tree_ = Tree(
#                self.n_features_in_,
#                np.array(
#                    [n_classes_],
#                    dtype=np.intp),
#                self.n_outputs_)
#            est_i.tree_.__setstate__(tree_i_state_dict)
#            estimators_.append(est_i)

        self._cached_estimators_ = estimators_
        return estimators_

    def _predict_proba(self, X):
        return dispatch(self, 'ensemble.RandomForestClassifier.predict_proba', {
            'onedal': self.__class__._onedal_predict_proba,
            'sklearn': sklearn_RandomForestClassifier._predict_proba,
        }, X)

    def _onedal_cpu_supported(self, method_name, *data):
        #if method_name in ['ensemble.RandomForestClassifier.predict',
        #                   'ensemble.RandomForestClassifier.predict_proba']:
        #    return hasattr(self, '_onedal_estimator')
        return True

    def _onedal_gpu_supported(self, method_name, *data):
        pass

    def _onedal_fit(self, X, y, sample_weight=None, queue=None):
        onedal_params = {
            'n_estimators': self.n_estimators,
            'criterion': self.criterion,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf':self.min_weight_fraction_leaf,
            'max_features': self.max_features,
            'max_leaf_nodes': self.max_leaf_nodes,
            'min_impurity_decrease': self.min_impurity_decrease,
            'bootstrap': self.bootstrap,
            'oob_score': self.oob_score,
            'n_jobs': self.n_jobs,
            'random_state': self.random_state,
            'verbose': self.verbose,
            'warm_start': self.warm_start,
            'class_weight': self.class_weight,
        }
        self._onedal_estimator = onedal_RandomForestClassifier(**onedal_params)
        self._onedal_estimator.fit(X, y, sample_weight, queue=queue)

        self._save_attributes()

    def _onedal_predict(self, X, queue=None):
        return self._onedal_estimator.predict(X, queue=queue)

    def _onedal_predict_proba(self, X, queue=None):
        pass


# class RandomForestRegressor(sklearn_RandomForestRegressor, BaseRandomForest):
#     __doc__ = sklearn_RandomForestRegressor.__doc__
# 
#     def __init__(self,
#                  n_estimators=100, *,
#                  criterion="squared_error",
#                  max_depth=None,
#                  min_samples_split=2,
#                  min_samples_leaf=1,
#                  min_weight_fraction_leaf=0.,
#                  max_features="auto",
#                  max_leaf_nodes=None,
#                  min_impurity_decrease=0.,
#                  bootstrap=True,
#                  oob_score=False,
#                  n_jobs=None,
#                  random_state=None,
#                  verbose=0,
#                  warm_start=False,
#                  ccp_alpha=0.0,
#                  max_samples=None,
#                  maxBins=256,
#                  minBinSize=1):
#         super().__init__(
#             n_estimators=n_estimators,
#             criterion=criterion,
#             max_depth=max_depth,
#             min_samples_split=min_samples_split,
#             min_samples_leaf=min_samples_leaf,
#             min_weight_fraction_leaf=min_weight_fraction_leaf,
#             max_features=max_features,
#             max_leaf_nodes=max_leaf_nodes,
#             min_impurity_decrease=min_impurity_decrease,
#             bootstrap=bootstrap,
#             oob_score=oob_score,
#             n_jobs=n_jobs,
#             random_state=random_state,
#             verbose=verbose,
#             warm_start=warm_start
#         )
#         self.ccp_alpha = ccp_alpha
#         self.max_samples = max_samples
#         self.maxBins = maxBins
#         self.minBinSize = minBinSize
#         self.min_impurity_split = None
# 
# 
#     def fit(self, X, y, sample_weight=None):
#         pass
# 
# 
#     def predict(self, X):
#         pass
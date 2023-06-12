# ===============================================================================
# Copyright 2023 Intel Corporation
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
# ===============================================================================

import pytest
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from daal4py.sklearn._utils import daal_check_version, sklearn_check_version

if daal_check_version((2023, 'P', 200)):
    from onedal.kmeans import KMeans
    from onedal.tests.utils._device_selection import get_queues
    from onedal.kmeans_init import kmeans_plusplus as init_internal

    from sklearn.cluster import kmeans_plusplus as init_external
    from sklearn.datasets import load_breast_cancer
    from sklearn.metrics import davies_bouldin_score
    from sklearn.model_selection import train_test_split

    from sklearn.neighbors import NearestNeighbors

    def generate_dataset(n_dim, n_cluster, n_points = None, seed = 777):
        # We need some reference value of points for each cluster
        n_points = (n_dim * n_cluster) if n_points is None else n_points

        # Creating generator and generating cluster points
        gen = np.random.Generator(np.random.MT19937(seed))
        cs = gen.uniform(low = -1.0, high = +1.0, size = (n_cluster, n_dim))

        # Finding variances for each cluster using 2 sigma criteria
        # It ensures that point is in the Voronoi cell of cluster
        d, i = NearestNeighbors(n_neighbors = 2).fit(cs).kneighbors(cs)
        assert_array_equal(i[:, 0], np.arange(n_cluster))
        vs = d[:, 1] / 2

        # Generating dataset
        gen_one = lambda c: gen.normal(loc = cs[c, :], scale = vs[c], size = (n_points, n_dim))
        data = [ gen_one(c) for c in range(n_cluster) ]
        data = np.concatenate(data, axis = 0)
        gen.shuffle(data, axis = 0)

        return (cs, vs, data)

    @pytest.mark.parametrize('queue', get_queues())
    @pytest.mark.parametrize('dtype', [np.float32, np.float64])
    @pytest.mark.parametrize('n_dim', [3, 8, 65])
    @pytest.mark.parametrize('n_cluster', [7, 64, 128])
    @pytest.mark.parametrize('pipeline', [ 'implicit', 'external', 'internal'])
    def test_generated_dataset(queue, dtype, n_dim, n_cluster, pipeline):
        seed = 777 * n_dim * n_cluster**2
        cs, vs, X = generate_dataset(n_dim, n_cluster, seed = seed)

        if pipeline == 'external':
            init_data, _ = init_external(X, n_cluster)
            m = KMeans(n_cluster, init = init_data, max_iter = 3)
        elif pipeline == 'internal':
            init_data, _ = init_internal(X, n_cluster, queue = queue)
            m = KMeans(n_cluster, init = init_data, max_iter = 3)
        else:
            m = KMeans(n_cluster, init = 'k-means++', max_iter = 3)

        m.fit(X, queue = queue)

        rs_centroids = m.cluster_centers_
        d, _ = NearestNeighbors(n_neighbors = 1).fit(cs).kneighbors(rs_centroids)
        # We have applied 2 sigma rule once
        desired_accuracy = int(0.9545 * n_cluster)
        correctness = d.reshape(-1) <= (vs * 2)
        exp_accuracy = np.count_nonzero(correctness)

        assert desired_accuracy <= exp_accuracy
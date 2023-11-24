/*******************************************************************************
* Copyright 2023 Intel Corporation
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/
#include <iostream>
#include <pybind11/pybind11.h>

#include "oneapi/dal/common.hpp"
#include "oneapi/dal/table/common.hpp"

#include "onedal/common.hpp"
#include "onedal/common/dtype_dispatcher.hpp"

namespace py = pybind11;

namespace oneapi::dal::python {

inline void instantiate_data_type(py::module& pm) {
    py::enum_<dal::data_type> py_dtype(pm, "dtype");
    py_dtype.value("int8", dal::data_type::int8);
    py_dtype.value("int16", dal::data_type::int16);
    py_dtype.value("int32", dal::data_type::int32);
    py_dtype.value("int64", dal::data_type::int64);
    py_dtype.value("uint8", dal::data_type::uint8);
    py_dtype.value("uint16", dal::data_type::uint16);
    py_dtype.value("uint32", dal::data_type::uint32);
    py_dtype.value("uint64", dal::data_type::uint64);
    py_dtype.value("float32", dal::data_type::float32);
    py_dtype.value("float64", dal::data_type::float64);
    py_dtype.export_values();
}

inline void instantiate_feature_type(py::module& pm) {
    py::enum_<dal::feature_type> py_ftype(pm, "ftype");
    py_ftype.value("ratio", dal::feature_type::ratio);
    py_ftype.value("nominal", dal::feature_type::nominal);
    py_ftype.value("ordinal", dal::feature_type::ordinal);
    py_ftype.value("interval", dal::feature_type::interval);
    py_ftype.export_values();
}

ONEDAL_PY_INIT_MODULE(dtype_dispatcher) {
    (void)instantiate_feature_type(m);
    (void)instantiate_data_type(m);
} // ONEDAL_PY_INIT_MODULE(dtype_dispatcher)

} // namespace oneapi::dal::python

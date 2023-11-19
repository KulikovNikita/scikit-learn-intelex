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

#pragma once

#include "onedal/common.hpp"

#include "oneapi/dal/table/homogen.hpp"

namespace py = pybind11;

namespace oneapi::dal::python::data_management {

template <typename Type>
dal::array<Type> get_data(const dal::homogen_table& table);

void instantiate_homogen_table(py::module& pm);

} // namespace oneapi::dal::python::data_management
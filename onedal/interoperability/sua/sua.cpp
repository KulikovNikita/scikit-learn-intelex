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

#include "onedal/interoperability/sua/sua.hpp"
#include "onedal/interoperability/sua/sua_and_array.hpp"
#include "onedal/interoperability/sua/sua_and_table.hpp"
#include "onedal/interoperability/sua/dtype_conversion.hpp"

namespace oneapi::dal::python::interoperability {

void instantiate_sua_interoperability(py::module& pm) {
    auto sub_module = pm.def_submodule("sua");
    sua::instantiate_sua_and_array(sub_module);
    sua::instantiate_sua_dtype_convert(sub_module);
    sua::instantiate_sua_and_homogen_table(sub_module);
}

} // namespace oneapi::dal::python::interoperability
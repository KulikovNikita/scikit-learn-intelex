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

#include "onedal/interoperability/sua/sua.hpp"
#include "onedal/interoperability/buffer/buffer.hpp"
#include "onedal/interoperability/dlpack/dlpack.hpp"

#include "onedal/interoperability/dtype_conversion.hpp"

namespace oneapi::dal::python {

ONEDAL_PY_INIT_MODULE(interoperability);

} // namespace oneapi::dal::python

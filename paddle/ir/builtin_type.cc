// Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "paddle/ir/builtin_type.h"

namespace ir {
const ir::Type& DenseTensorType::dtype() const { return storage()->dtype_; }

const ir::DenseTensorTypeStorage::Dim& DenseTensorType::dim() const {
  return storage()->dims_;
}

const ir::DenseTensorTypeStorage::DataLayout& DenseTensorType::data_layout()
    const {
  return storage()->layout_;
}

const ir::DenseTensorTypeStorage::LoD& DenseTensorType::lod() const {
  return storage()->lod_;
}

const size_t& DenseTensorType::offset() const { return storage()->offset_; }
}  // namespace ir

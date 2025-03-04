# Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
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

import sys
import unittest

import numpy as np

sys.path.append("../")
from eager_op_test import OpTest

import paddle
from paddle.fluid import core


class TestSequencePadOp(OpTest):
    def set_attr(self):
        self.x_shape = [12, 10]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = [1.0]
        self.padded_length = -1
        self.dtype = 'float64'

    def set_data(self):
        x_data = np.random.uniform(0.1, 0.5, self.x_shape).astype(self.dtype)
        pad_value_data = np.array(self.pad_value).astype(self.dtype)
        self.inputs = {
            'X': (x_data, self.x_len_lod),
            'PadValue': pad_value_data,
        }
        self.attrs = {'padded_length': self.padded_length}

    def compute(self):
        # get padded length
        padded_length = self.padded_length
        x_len_lod_0 = self.x_len_lod[0]
        if padded_length == -1:
            max_seq_len = 0
            for l in x_len_lod_0:
                max_seq_len = max(max_seq_len, l)
            padded_length = max_seq_len

        # do padding
        x_data = self.inputs['X'][0]
        pad_value_data = self.inputs['PadValue']
        if pad_value_data.shape == (1,):
            pad_value_data = np.broadcast_to(
                pad_value_data, shape=x_data.shape[1:]
            )
        padded_sequences = []
        start_idx = 0
        for l in x_len_lod_0:
            end_idx = start_idx + l
            seq = x_data[start_idx:end_idx]
            to_pad_len = padded_length - l
            for _ in range(to_pad_len):
                seq = np.append(seq, pad_value_data[np.newaxis, :], axis=0)
            padded_sequences.append(seq)
            start_idx = end_idx

        out_data = np.array(padded_sequences)
        length = np.array(self.x_len_lod[0]).reshape(-1)
        self.outputs = {'Out': out_data, 'Length': length}

    def setUp(self):
        self.op_type = 'sequence_pad'
        self.set_attr()
        self.set_data()
        self.compute()

    def test_check_output(self):
        self.check_output(check_dygraph=False)

    def test_check_grad(self):
        self.check_grad(["X"], "Out", check_dygraph=False)


class TestSequencePadOp2(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 10]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = np.random.random(10)
        self.padded_length = -1
        self.dtype = 'float64'


class TestSequencePadOp3(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 10]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = [1.0]
        self.padded_length = 7
        self.dtype = 'float64'


class TestSequencePadOp4(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 10]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = np.random.random(10)
        self.padded_length = 7
        self.dtype = 'float64'


class TestSequencePadOp5(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 2, 5]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = [1.0]
        self.padded_length = -1
        self.dtype = 'float64'


class TestSequencePadOp6(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 2, 5]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = np.random.random((2, 5))
        self.padded_length = -1
        self.dtype = 'float64'


class TestSequencePadOp7(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 2, 5]
        self.x_len_lod = [[2, 3, 4, 3]]
        self.pad_value = [1.0]
        self.padded_length = 7
        self.dtype = 'float64'


class TestSequencePadOp8(TestSequencePadOp):
    def set_attr(self):
        self.x_shape = [12, 2, 5]
        self.x_len_lod = [[0, 8, 0, 4, 0]]
        self.pad_value = [1.0]
        self.padded_length = 10
        self.dtype = 'float64'


class TestSequencePadOpError(unittest.TestCase):
    def test_error(self):
        def test_x_variable():
            # the input x type must be Variable
            x = np.random.random((2, 4)).astype("float32")

            pad_value = paddle.assign(np.array([0.0], dtype=np.float32))
            paddle.static.nn.sequence_lod.sequence_pad(x=x, pad_value=pad_value)

        self.assertRaises(TypeError, test_x_variable)

        def test_pad_value_variable():
            x1 = paddle.static.data(
                name='x1', shape=[-1, 10, 5], dtype='float32', lod_level=1
            )
            pad_value1 = np.array([0.0], dtype=np.float32)
            paddle.static.nn.sequence_lod.sequence_pad(
                x=x1, pad_value=pad_value1
            )

        self.assertRaises(TypeError, test_pad_value_variable)

        def test_dtype():
            x2 = paddle.static.data(
                name='x2', shape=[-1, 10, 5], dtype='int16', lod_level=1
            )

            pad_value2 = paddle.assign(np.array([0.0], dtype=np.int32))
            paddle.static.nn.sequence_lod.sequence_pad(
                x=x2, pad_value=pad_value2
            )

        self.assertRaises(TypeError, test_dtype)

    def test_length_dtype(self):
        x = paddle.static.data(
            name='x', shape=[10, 5], dtype='float32', lod_level=1
        )

        pad_value = paddle.assign(np.array([0.0], dtype=np.float32))
        out, length = paddle.static.nn.sequence_lod.sequence_pad(
            x=x, pad_value=pad_value
        )
        # check if the dtype of length is int64 in compile time
        self.assertEqual(length.dtype, core.VarDesc.VarType.INT64)


if __name__ == '__main__':
    unittest.main()

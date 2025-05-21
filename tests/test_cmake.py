import paddle

import custom_relu_setup_cmake

test_tensor = paddle.randn([4, 10], dtype='float32')
print(test_tensor)

out = custom_relu_setup_cmake.custom_relu(test_tensor)
print(out)
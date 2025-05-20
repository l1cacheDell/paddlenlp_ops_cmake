#include "paddle/extension.h"

template <typename data_t>
__global__ void relu_cuda_forward_kernel(const data_t* x,
                                         data_t* y,
                                         int64_t num) {
  int64_t gid = blockIdx.x * blockDim.x + threadIdx.x;
  for (int64_t i = gid; i < num; i += blockDim.x * gridDim.x) {
    y[i] = max(x[i], static_cast<data_t>(0.));
  }
}

std::vector<paddle::Tensor> relu_cuda_forward(const paddle::Tensor& x) {

  auto out = paddle::empty_like(x);

  int64_t numel = x.numel();
  int64_t block = 512;
  int64_t grid = (numel + block - 1) / block;
  PD_DISPATCH_FLOATING_TYPES(
      x.type(), "relu_cuda_forward_kernel", ([&] {
        relu_cuda_forward_kernel<data_t><<<grid, block, 0, x.stream()>>>(
            x.data<data_t>(), 
            out.data<data_t>(), 
            numel);
      }));

  return {out};
}

// 维度推导
std::vector<std::vector<int64_t>> ReluInferShape(std::vector<int64_t> x_shape) {
  return {x_shape};
}

// 类型推导
std::vector<paddle::DataType> ReluInferDtype(paddle::DataType x_dtype) {
  return {x_dtype};
}

PD_BUILD_OP(custom_relu)
    .Inputs({"X"})
    .Outputs({"Out"})
    .SetKernelFn(PD_KERNEL(relu_cuda_forward))
    .SetInferShapeFn(PD_INFER_SHAPE(ReluInferShape))
    .SetInferDtypeFn(PD_INFER_DTYPE(ReluInferDtype));
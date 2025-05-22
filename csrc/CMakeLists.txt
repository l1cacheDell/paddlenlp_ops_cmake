cmake_minimum_required(VERSION 3.18)

# 定义一个 OBJECT 库或者 SHARED 库都可以
# OBJECT 库适合一次性链接到多个最终 target
add_library(relu_obj OBJECT relu.cu)
target_compile_options(relu_obj
  PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:${CUDA_NVCC_FLAGS}>
)
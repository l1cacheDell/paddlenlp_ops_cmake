from paddle.utils.cpp_extension import CUDAExtension, setup

NVCC_FLAGS = [
    "-O3",
    "-std=c++17",
    "-U__CUDA_NO_HALF_OPERATORS__",
    "-U__CUDA_NO_HALF_CONVERSIONS__",
    "--use_fast_math",
    "--threads=8",
    "-Xptxas=-v",
    "-diag-suppress=174", # suppress the specific warning
    # "-G",        # very important notice: you should turn this button off, when finish debuging
    # "-g"
]

NVCC_FLAGS += ["-gencode", f"arch=compute_89,code=sm_89"]

setup(
    name='custom_relu_setup',
    ext_modules=CUDAExtension(
        sources=['csrc/relu.cu'],
        extra_compile_args={
            "nvcc": NVCC_FLAGS,
        },
    ),
    
)
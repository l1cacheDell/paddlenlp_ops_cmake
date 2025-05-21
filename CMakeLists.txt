cmake_minimum_required(VERSION 3.18)
project(custom_relu_setup LANGUAGES CXX CUDA)

# 指定 C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 开启 Release 模式下的优化
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# CUDA 编译选项
set(CUDA_NVCC_FLAGS
    -O3
    -U__CUDA_NO_HALF_OPERATORS__
    -U__CUDA_NO_HALF_CONVERSIONS__
    --use_fast_math
    -Xptxas=-v
    -diag-suppress=174
    -gencode arch=compute_89,code=sm_89
)

# TODO, paddle的prefix path也在这里添加一下
set(CMAKE_PREFIX_PATH
    "${CMAKE_PREFIX_PATH}"
    "/usr/local/lib/python3.12/dist-packages/pybind11/share/cmake/pybind11"
)

# 查找 Paddle 的头文件和库（假设已安装并提供了 CMake 包）
# find_package(Paddle REQUIRED)   
# 查找 CUDA（一般系统自带）
find_package(CUDA REQUIRED)
find_package(pybind11 REQUIRED)

# 源码列表
set(SRC
    csrc/relu.cu
)

add_definitions("-DPADDLE_WITH_CUDA")

# 生成一个共享库，名字和 setup.py 中给的 name 保持一致
add_library(${PROJECT_NAME} SHARED csrc/relu.cu)
target_compile_options(${PROJECT_NAME}
  PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:${CUDA_NVCC_FLAGS}>
)

# 链接 Paddle 和 CUDA 运行时
include_directories(/usr/local/lib/python3.12/dist-packages/paddle/include)
include_directories(${pybind11_INCLUDE_DIRS})

# 把 lib 搜索路径指向两个目录：libs 和 base
find_library(PADDLE_LIB
  NAMES paddle            # CMake 会在每个 PATH 里查找 libpaddle.so
  PATHS
    /usr/local/lib/python3.12/dist-packages/paddle/libs
    /usr/local/lib/python3.12/dist-packages/paddle/base
  # 指明必须找到
  REQUIRED
)

message(STATUS "PADDLE_LIB = ${PADDLE_LIB}")

target_link_libraries(${PROJECT_NAME}
    PRIVATE
    ${PADDLE_LIB}      # Paddle CMake 包导出的 target
    ${CUDA_CUDART_LIBRARY}
)

# 输出 .so 到 Python 扩展模块的目录
# build_ext 会将 build_lib 设置成你安装时的目标目录
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        PREFIX ""                  # 不要前缀 lib
        OUTPUT_NAME "${PROJECT_NAME}"
        SUFFIX ".so"
)
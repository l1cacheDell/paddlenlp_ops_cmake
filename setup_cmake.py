from paddle.utils.cpp_extension import CUDAExtension, setup
import os
import sys
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess

class CMakeBuild(_build_ext):
    def run(self):
        for ext in self.extensions:
            # 构建临时目录，和 setuptools 一致
            build_temp = os.path.join(self.build_temp, ext.name)
            os.makedirs(build_temp, exist_ok=True)

            # CMake 配置参数：把 .so 输出到 build_lib
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            cmake_args = [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
                f"-DPYTHON_EXECUTABLE={sys.executable}",
                "-DCMAKE_BUILD_TYPE=Release",
            ]
            # 调用 cmake 和 cmake --build
            subprocess.check_call(["cmake", os.path.abspath(".")] + cmake_args, cwd=build_temp)
            subprocess.check_call(["cmake", "--build", ".", "--config", "Release", "--", "-j8"], cwd=build_temp)

        # 2) CMake 完成后，交给 Paddle 的 build_ext（包含 stub 注入等逻辑）
        super().run()

ext_modules = [
    CUDAExtension(name="custom_relu_setup_cmake", sources=[])
]

setup(
    name='custom_relu_setup_cmake',
    version='0.0.0',
    author='dyz',
    description="Paddle custom ReLU op built via CMake",
    ext_modules=ext_modules,
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
)
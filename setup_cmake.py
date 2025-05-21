from paddle.utils.cpp_extension import CUDAExtension, setup
import os
import sys
from setuptools import Extension, find_packages
from setuptools.command.build_ext import build_ext
import subprocess


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        # sources 必须给一个空列表，交给 CMake 处理
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        # 确保 CMake 可用
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake is required to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name))
        )
        # 构建参数：设置库输出目录到 extdir
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            "-DCMAKE_BUILD_TYPE=Release",
        ]
        build_args = ["--config", "Release", "--", "-j8"]

        build_temp = os.path.join(self.build_temp, ext.name)
        os.makedirs(build_temp, exist_ok=True)

        # 1. 生成构建文件
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=build_temp
        )
        # 2. 真正编译
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=build_temp
        )

setup(
    name='custom_relu_setup',
    version='0.0.0',
    author='dyz',
    description="Paddle custom ReLU op built via CMake",
    ext_modules=[CMakeExtension("custom_relu_setup")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
)
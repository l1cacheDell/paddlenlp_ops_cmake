from paddle.utils.cpp_extension import CUDAExtension, setup
from paddle.utils.cpp_extension.extension_utils import load_op_meta_info_and_register_op, _custom_api_content
from paddle.utils.cpp_extension import extension_utils
import os
import glob
import sys
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess
import textwrap

def custom_write_stub_cmake(resource, pyfile):
    """
    Customized write_stub function to allow us to inject generated python
    api codes into egg python file.
    """
    _stub_template = textwrap.dedent(
        """
        {custom_api}

        import os
        import sys
        import types
        import paddle
        import importlib.abc
        import importlib.util

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        so_path = os.path.join(cur_dir, "{resource}")

        def __bootstrap__():
            assert os.path.exists(so_path)
            # load custom op shared library with abs path
            custom_ops = paddle.utils.cpp_extension.load_op_meta_info_and_register_op(so_path)

            if os.name == 'nt' or sys.platform.startswith('darwin'):
                # Cpp Extension only support Linux now
                mod = types.ModuleType(__name__)
            else:
                try:
                    spec = importlib.util.spec_from_file_location(__name__, so_path)
                    assert spec is not None
                    mod = importlib.util.module_from_spec(spec)
                    assert isinstance(spec.loader, importlib.abc.Loader)
                    spec.loader.exec_module(mod)
                except ImportError:
                    mod = types.ModuleType(__name__)

            for custom_op in custom_ops:
                setattr(mod, custom_op, eval(custom_op))

        __bootstrap__()

        """
    ).lstrip()

    # NOTE: To avoid importing .so file instead of python file because they have same name,
    # we rename .so shared library to another name, see EasyInstallCommand.
    filename, ext = os.path.splitext(resource)
    resource = filename + "_pd_" + ext

    print(f"[[[{resource}]]]")
    print(f"[[[{pyfile}]]]")
    print(666666)
    print("努力奋斗")


    api_content = []

    # TODO: 这个地方需要看看怎么灵活用
    so_path = "build/custom_relu_setup_cmake/lib.linux-x86_64-cpython-312/custom_relu_setup_cmake.so"

    new_custom_ops = load_op_meta_info_and_register_op(so_path)
    for op_name in new_custom_ops:
        api_content.append(_custom_api_content(op_name))
    print(
        f"Received len(custom_op) = {len(new_custom_ops)}, using custom operator"
    )

    with open(pyfile, 'w') as f:
        f.write(
            _stub_template.format(
                resource=resource, custom_api='\n\n'.join(api_content)
            )
        )

# hook
extension_utils.custom_write_stub = custom_write_stub_cmake


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

    def get_ext_filename(self, fullname):
        # fullname：扩展模块的「完整名字」，如 "custom_relu_setup_cmake"
        filename = super().get_ext_filename(fullname)
        # 默认可能是 "custom_relu_setup_cmake.cpython-312-x86_64-linux-gnu.so"
        base, ext = os.path.splitext(filename)

        # 示例：把它改为只有 module 名 + .so
        new_name = fullname + ext  # ".so" 保留
        return new_name

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
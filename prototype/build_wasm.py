"""
构建 WASM 模块的辅助脚本

如果系统安装了 wabt (WebAssembly Binary Toolkit)，
可以使用 wat2wasm 将 WAT 文件转换为 WASM 二进制文件。

如果没有 wat2wasm，我们创建一个最小的 WASM 二进制文件。
"""

from pathlib import Path


def create_minimal_wasm() -> bytes:
    """
    创建一个最小的有效 WASM 模块
    
    这是一个手工构造的最小 WASM 模块，包含：
    - WASM 头部 (magic number + version)
    - 一个空的代码段
    """
    # WASM 文件格式：
    # Magic number: 0x00 0x61 0x73 0x6D (\0asm)
    # Version: 0x01 0x00 0x00 0x00 (version 1)
    
    wasm_bytes = bytearray([
        0x00, 0x61, 0x73, 0x6D,  # magic number "\0asm"
        0x01, 0x00, 0x00, 0x00,  # version 1
    ])
    
    # Type section (section id = 1)
    # 定义一个函数类型：() -> ()
    wasm_bytes.extend([
        0x01,  # section id: Type
        0x04,  # section size: 4 bytes
        0x01,  # number of types: 1
        0x60,  # func type
        0x00,  # number of parameters: 0
        0x00,  # number of results: 0
    ])
    
    # Function section (section id = 3)
    # 声明一个函数使用 type 0
    wasm_bytes.extend([
        0x03,  # section id: Function
        0x02,  # section size: 2 bytes
        0x01,  # number of functions: 1
        0x00,  # function 0 uses type 0
    ])
    
    # Export section (section id = 7)
    # 导出一个名为 "main" 的函数
    wasm_bytes.extend([
        0x07,  # section id: Export
        0x08,  # section size: 8 bytes
        0x01,  # number of exports: 1
        0x04,  # length of export name: 4
        0x6D, 0x61, 0x69, 0x6E,  # export name: "main"
        0x00,  # export kind: function
        0x00,  # export function index: 0
    ])
    
    # Code section (section id = 10)
    # 定义函数体（空函数）
    wasm_bytes.extend([
        0x0A,  # section id: Code
        0x04,  # section size: 4 bytes
        0x01,  # number of function bodies: 1
        0x02,  # body size: 2 bytes
        0x00,  # local count: 0
        0x0B,  # end instruction
    ])
    
    return bytes(wasm_bytes)


def build_wasm_from_wat(wat_file: Path, output_file: Path) -> bool:
    """
    尝试使用 wat2wasm 转换 WAT 到 WASM
    
    如果失败，返回 False
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ['wat2wasm', str(wat_file), '-o', str(output_file)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Converted {wat_file} to {output_file}")
            return True
        else:
            print(f"wat2wasm failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("wat2wasm not found. Install WABT toolkit or use minimal WASM.")
        return False


def main():
    # 尝试转换 WAT 文件
    examples_dir = Path(__file__).parent / 'examples'
    wat_file = examples_dir / 'simple.wat'
    wasm_file = examples_dir / 'simple.wasm'
    
    examples_dir.mkdir(exist_ok=True)
    
    if wat_file.exists():
        success = build_wasm_from_wat(wat_file, wasm_file)
        if success:
            return
    
    # 如果失败，创建最小 WASM 模块
    print("Creating minimal WASM module...")
    minimal_wasm = create_minimal_wasm()
    
    with open(wasm_file, 'wb') as f:
        f.write(minimal_wasm)
    
    print(f"✓ Created minimal WASM: {wasm_file} ({len(minimal_wasm)} bytes)")


if __name__ == '__main__':
    main()


"""
.any 文件格式原型 - 主程序

提供创建、读取、执行 .any 文件的功能
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import wasmtime

from any_format import AnyFile


class AnyFileRunner:
    """运行 .any 文件的解释器"""

    def __init__(self, any_file: AnyFile):
        self.any_file = any_file
        self.engine = wasmtime.Engine()
        self.store = wasmtime.Store(self.engine)
        
    def run(self, command: str = "extract") -> Optional[bytes]:
        """
        执行 WASM 模块
        
        Args:
            command: 要执行的命令 (extract, info, list, etc.)
        
        Returns:
            执行结果（字节流）
        """
        try:
            # 加载 WASM 模块
            module = wasmtime.Module(self.engine, self.any_file.wasm_module)
            
            # 创建内存实例
            memory_type = wasmtime.MemoryType(wasmtime.Limits(1, 100))
            memory = wasmtime.Memory(self.store, memory_type)
            
            # 将数据写入 WASM 内存
            data_ptr = 0
            data = self.any_file.data
            if len(data) > 0:
                memory.write(self.store, data, data_ptr)
            
            # 创建导入对象
            imports = []
            
            # 实例化模块
            instance = wasmtime.Instance(self.store, module, imports)
            
            # 获取导出的函数
            exports = instance.exports(self.store)
            
            # 根据命令执行不同的函数
            if command == "extract":
                # 提取数据
                return self.any_file.data
            elif command == "info":
                # 返回元数据信息
                import json
                return json.dumps(self.any_file.metadata, indent=2, ensure_ascii=False).encode('utf-8')
            else:
                print(f"Unknown command: {command}")
                return None
                
        except Exception as e:
            print(f"Error running WASM: {e}", file=sys.stderr)
            return None


def create_any_file(
    data_file: Path,
    wasm_file: Path,
    output: Path,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """创建 .any 文件"""
    print(f"Creating .any file from:")
    print(f"  Data: {data_file}")
    print(f"  WASM: {wasm_file}")
    
    # 读取数据文件
    with open(data_file, 'rb') as f:
        data = f.read()
    
    # 读取 WASM 模块
    with open(wasm_file, 'rb') as f:
        wasm_module = f.read()
    
    # 创建元数据
    metadata = {
        "name": name or data_file.name,
        "description": description or "",
        "original_filename": data_file.name,
        "original_size": len(data),
    }
    
    # 创建 .any 文件
    any_file = AnyFile.create(
        wasm_module=wasm_module,
        data=data,
        metadata=metadata
    )
    
    # 写入文件
    with open(output, 'wb') as f:
        f.write(any_file.to_bytes())
    
    print(f"\n✓ Created: {output}")
    print(f"  Size: {len(any_file.to_bytes())} bytes")
    print(f"  Data: {len(data)} bytes")
    print(f"  WASM: {len(wasm_module)} bytes")


def info_any_file(input_file: Path) -> None:
    """显示 .any 文件信息"""
    with open(input_file, 'rb') as f:
        data = f.read()
    
    any_file = AnyFile.from_bytes(data)
    
    print(f"File: {input_file}")
    print(f"Version: {any_file.header.version_major}.{any_file.header.version_minor}")
    print(f"Total Size: {len(data)} bytes")
    print(f"\nComponents:")
    print(f"  WASM Module: {any_file.header.wasm_size} bytes")
    print(f"  Data: {any_file.header.data_size} bytes")
    print(f"  Metadata: {any_file.header.metadata_size} bytes")
    print(f"\nMetadata:")
    import json
    print(json.dumps(any_file.metadata, indent=2, ensure_ascii=False))


def extract_any_file(input_file: Path, output: Optional[Path] = None) -> None:
    """提取 .any 文件内容"""
    with open(input_file, 'rb') as f:
        data = f.read()
    
    any_file = AnyFile.from_bytes(data)
    
    # 运行 WASM 模块执行提取
    runner = AnyFileRunner(any_file)
    extracted_data = runner.run("extract")
    
    if extracted_data is None:
        print("Failed to extract data", file=sys.stderr)
        return
    
    # 确定输出文件名
    if output is None:
        original_name = any_file.metadata.get("original_filename", "output.bin")
        output = Path(original_name)
    
    # 写入输出文件
    with open(output, 'wb') as f:
        f.write(extracted_data)
    
    print(f"✓ Extracted to: {output}")
    print(f"  Size: {len(extracted_data)} bytes")


def main():
    parser = argparse.ArgumentParser(
        description=".any 文件格式原型 - 基于 WebAssembly 的自解释文件",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建 .any 文件')
    create_parser.add_argument('data', type=Path, help='数据文件路径')
    create_parser.add_argument('wasm', type=Path, help='WASM 模块路径')
    create_parser.add_argument('-o', '--output', type=Path, required=True, help='输出 .any 文件路径')
    create_parser.add_argument('-n', '--name', help='文件名称')
    create_parser.add_argument('-d', '--description', help='文件描述')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='显示 .any 文件信息')
    info_parser.add_argument('file', type=Path, help='.any 文件路径')
    
    # extract 命令
    extract_parser = subparsers.add_parser('extract', help='提取 .any 文件内容')
    extract_parser.add_argument('file', type=Path, help='.any 文件路径')
    extract_parser.add_argument('-o', '--output', type=Path, help='输出文件路径')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_any_file(
            data_file=args.data,
            wasm_file=args.wasm,
            output=args.output,
            name=args.name,
            description=args.description
        )
    elif args.command == 'info':
        info_any_file(args.file)
    elif args.command == 'extract':
        extract_any_file(args.file, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

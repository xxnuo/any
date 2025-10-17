# .any 文件格式原型

基于 WebAssembly 的自解释文件格式原型实现。

## 概述

`.any` 是一种新型文件格式，它将数据和 WebAssembly 解释器打包在一起，实现文件的自我解释和提取。类似于自解压文件，但通过 WebAssembly 沙箱提供更高的安全性。

## 特性

- 📦 **自包含**: 文件包含数据和解释逻辑
- 🔒 **安全**: 基于 WebAssembly 沙箱执行
- 🎯 **简单**: 统一的文件格式，无需各种解压工具
- 🔍 **可检查**: 可以查看文件信息而不执行

## 文件格式

```
┌──────────────────┐
│   文件头 (36 B)  │  Magic: 0x414E5946 ("ANYF")
├──────────────────┤  Version, 各部分大小
│   WASM 模块      │  WebAssembly 解释器
├──────────────────┤
│   数据区         │  实际文件内容
├──────────────────┤
│   元数据 (JSON)  │  文件信息、属性等
└──────────────────┘
```

## 安装

```bash
# 进入原型目录
cd prototype

# 安装依赖（使用 uv）
uv sync
```

## 使用方法

### 1. 创建 .any 文件

```bash
# 准备 WASM 模块
uv run python build_wasm.py

# 创建 .any 文件
uv run python main.py create <数据文件> <WASM模块> -o <输出.any> [选项]

# 示例
uv run python main.py create examples/test_data.txt examples/simple.wasm \
    -o examples/test.any \
    -n "Test File" \
    -d "A test .any file"
```

**参数说明:**
- `数据文件`: 要打包的原始文件
- `WASM模块`: WebAssembly 解释器模块
- `-o, --output`: 输出的 .any 文件路径
- `-n, --name`: 文件名称（可选）
- `-d, --description`: 文件描述（可选）

### 2. 查看 .any 文件信息

```bash
uv run python main.py info <文件.any>

# 示例输出
File: examples/test.any
Version: 1.0
Total Size: 402 bytes

Components:
  WASM Module: 34 bytes
  Data: 216 bytes
  Metadata: 116 bytes

Metadata:
{
  "name": "Test File",
  "description": "A test .any file",
  "original_filename": "test_data.txt",
  "original_size": 216
}
```

### 3. 提取 .any 文件内容

```bash
uv run python main.py extract <文件.any> [-o <输出文件>]

# 示例
uv run python main.py extract examples/test.any -o output.txt
```

如果不指定输出文件名，将使用元数据中的原始文件名。

## 示例

完整的使用流程：

```bash
# 1. 构建 WASM 模块
uv run python build_wasm.py

# 2. 创建 .any 文件
uv run python main.py create examples/test_data.txt examples/simple.wasm \
    -o my_file.any \
    -n "My Document" \
    -d "Important document"

# 3. 查看文件信息
uv run python main.py info my_file.any

# 4. 提取文件内容
uv run python main.py extract my_file.any -o restored.txt

# 5. 验证文件一致性
diff examples/test_data.txt restored.txt
```

## 架构说明

### 核心模块

- **any_format.py**: 定义 .any 文件格式结构
  - `AnyFileHeader`: 文件头定义
  - `AnyFile`: 完整文件结构
  - 序列化/反序列化功能

- **main.py**: 主程序
  - `AnyFileRunner`: WASM 运行器
  - 创建、查看、提取命令实现

- **build_wasm.py**: WASM 构建工具
  - 支持从 WAT 转换 (需要 wabt 工具)
  - 内置最小 WASM 模块生成

### 安全性考虑

1. **沙箱执行**: WASM 在受限环境中运行
2. **内存隔离**: WASM 模块有独立的线性内存
3. **可审查**: 在执行前可以检查文件信息
4. **无系统调用**: WASM 模块不能直接访问系统资源

## 扩展方向

- [ ] 支持压缩（gzip, zstd）
- [ ] 支持加密和签名
- [ ] 支持多文件打包
- [ ] 更丰富的 WASM 接口（列表、搜索等）
- [ ] GUI 工具
- [ ] 浏览器支持（直接在浏览器中运行）

## 技术栈

- **Python 3.13+**: 主要编程语言
- **wasmtime**: WebAssembly 运行时
- **uv**: Python 包管理器

## 许可证

见根目录 LICENSE 文件


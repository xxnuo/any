"""
.any 文件格式定义

文件结构：
[文件头] [WASM模块] [数据区] [元数据]

文件头 (32 bytes):
- Magic Number (4 bytes): 0x414E5946 ("ANYF")
- Version (4 bytes): 主版本.次版本
- WASM Size (8 bytes): WASM模块大小
- Data Size (8 bytes): 数据区大小
- Metadata Size (8 bytes): 元数据大小
"""

import struct
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


MAGIC_NUMBER = 0x414E5946  # "ANYF"
VERSION_MAJOR = 1
VERSION_MINOR = 0
HEADER_SIZE = 36  # IIIQQQ = 4+4+4+8+8+8 = 36 bytes


@dataclass
class AnyFileHeader:
    """文件头结构"""
    magic: int
    version_major: int
    version_minor: int
    wasm_size: int
    data_size: int
    metadata_size: int

    def to_bytes(self) -> bytes:
        """转换为字节"""
        return struct.pack(
            '>IIIQQQ',  # 大端序
            self.magic,
            self.version_major,
            self.version_minor,
            self.wasm_size,
            self.data_size,
            self.metadata_size
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'AnyFileHeader':
        """从字节解析"""
        unpacked = struct.unpack('>IIIQQQ', data[:HEADER_SIZE])
        return cls(
            magic=unpacked[0],
            version_major=unpacked[1],
            version_minor=unpacked[2],
            wasm_size=unpacked[3],
            data_size=unpacked[4],
            metadata_size=unpacked[5]
        )

    def validate(self) -> bool:
        """验证文件头"""
        return self.magic == MAGIC_NUMBER


@dataclass
class AnyFile:
    """完整的 .any 文件结构"""
    header: AnyFileHeader
    wasm_module: bytes
    data: bytes
    metadata: Dict[str, Any]

    def to_bytes(self) -> bytes:
        """序列化为字节"""
        metadata_bytes = json.dumps(self.metadata, ensure_ascii=False).encode('utf-8')
        
        # 更新 header 中的大小
        self.header.wasm_size = len(self.wasm_module)
        self.header.data_size = len(self.data)
        self.header.metadata_size = len(metadata_bytes)
        
        return (
            self.header.to_bytes() +
            self.wasm_module +
            self.data +
            metadata_bytes
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'AnyFile':
        """从字节反序列化"""
        # 解析文件头
        header = AnyFileHeader.from_bytes(data[:HEADER_SIZE])
        
        if not header.validate():
            raise ValueError(f"Invalid magic number: {hex(header.magic)}")
        
        # 解析各个部分
        offset = HEADER_SIZE
        
        wasm_module = data[offset:offset + header.wasm_size]
        offset += header.wasm_size
        
        file_data = data[offset:offset + header.data_size]
        offset += header.data_size
        
        metadata_bytes = data[offset:offset + header.metadata_size]
        metadata = json.loads(metadata_bytes.decode('utf-8'))
        
        return cls(
            header=header,
            wasm_module=wasm_module,
            data=file_data,
            metadata=metadata
        )

    @classmethod
    def create(
        cls,
        wasm_module: bytes,
        data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'AnyFile':
        """创建新的 .any 文件"""
        if metadata is None:
            metadata = {}
        
        header = AnyFileHeader(
            magic=MAGIC_NUMBER,
            version_major=VERSION_MAJOR,
            version_minor=VERSION_MINOR,
            wasm_size=len(wasm_module),
            data_size=len(data),
            metadata_size=0  # 将在 to_bytes 时计算
        )
        
        return cls(
            header=header,
            wasm_module=wasm_module,
            data=data,
            metadata=metadata
        )


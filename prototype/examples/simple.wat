;; 简单的 WebAssembly 模块
;; 这个模块是 .any 文件的默认解释器

(module
  ;; 导入内存（可选）
  (memory (export "memory") 1)
  
  ;; 简单的 identity 函数，用于验证模块加载成功
  (func $identity (param $x i32) (result i32)
    local.get $x
  )
  (export "identity" (func $identity))
  
  ;; 数据处理函数
  (func $process_data (param $ptr i32) (param $len i32) (result i32)
    ;; 简单返回数据长度
    local.get $len
  )
  (export "process_data" (func $process_data))
)


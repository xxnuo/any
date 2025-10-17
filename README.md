# *.any

A file format containing content of files in any format: *.any based on WebAssembly.

## Inspiration

设想一个文件格式，支持输出自己的内容、属性等。这样就不需要下载各种复杂的解压、执行工具了。

类似于自解压文件，但是传统自解压文件存在执行安全问题，比如病毒、木马等。

所以必须用一种新的方式来实现，比如基于更安全的虚拟机的方式。那么就是 WebAssembly 技术了。

一种基于 WebAssembly 的文件格式，可以实现文件的自我解释和执行。

由系统自带或者手动安装一次自己信任的解释器，然后就可以直接运行任何文件了。

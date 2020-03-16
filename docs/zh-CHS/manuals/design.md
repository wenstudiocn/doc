---
title: The design of Defold
brief: The philosophy behind Defold's design
---

# The design of Defold

Defold was created with the following goals:

- To be a complete professional turn-key production platform for game teams.
- To be simple and clear, providing explicit solutions to common game development architectural and workflow problems.
- To be a blazing fast development platform ideal for iterative game development.
- To be high-performance in runtime.
- To be truly multi-platform.

The design of the editor and engine is carefully crafted to reach those goals. Some of our design decisions differ from what you may be used to if you have experience with other platforms, for example:

- We require static declaration of the resource tree and all naming. This requires some initial effort from you, but helps the development process tremendously in the long run.
- We encourage message passing between simple encapsulated entities.
- There is no object orientation inheritance.
- Our APIs are asynchronous.
- The rendering pipeline is code driven and fully customizable.
- All our resource files are in simple plain text formats, optimally structured for Git merges as well as import and processing with external tools.
- Resources can be changed and hot reloaded into a running game allowing for extremely fast iteration and experimentation.

# Defold 的设计

Defold 作为游戏引擎具有以下目标:

- 成为游戏团队一个完整而专业的生产交付平台.
- 用法简单而明了, 为常见的游戏开发架构和工作流程问题提供明确的解决方案.
- 成为迭代游戏开发的理想的快速开发平台.
- 运行时具有高性能.
- 真正意义的多平台支持.

编辑器和引擎经过精心设计以实现这些目标. 我们有些设计原则可能不同于你已知道的, 如果你有其他平台的使用经验的话. 例如:

- 我们需要静态声明资源树以及所有命名. 这需要你在开始时做出一些工作, 但从长远来看, 却会极大地有助于开发进程.
- 我们鼓励在简单封装的实体间传递消息.
- 没有面向对象式的继承.
- 异步 API.
- 渲染管线是代码驱动并且完全可定制化.
- 资源文件以文本格式存储, 针对 git 合并和利用外部工具导入和处理的最佳结构.
- 更改后的资源可热加载到正在运行的游戏进程中, 从而可以极快的迭代和实验.

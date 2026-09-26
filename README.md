这是基于 [YueMoon99/BlenderBatchRenderer] 的个人修改版，仅用于个人备份学习。
1. 修复了“预计剩余时间（ETA）”计算错误的 Bug
原版在渲染中断后重新开始，由于 rendered_frames 计数器被清零，导致算出的剩余时间极其离谱。修改后，程序会直接扫描输出文件夹中实际存在的帧文件数量，结合最近一帧的真实耗时来动态计算 ETA。完美适配“删除部分错误帧后继续渲染”的工作流。

2. 修复了进程残留导致的“拒绝访问”问题
原版在异常退出或停止渲染时，偶尔会留下僵尸进程锁死 exe 文件。本次修改：
去除了容易导致退出冲突的“系统托盘（QSystemTrayIcon）”功能，改为直接彻底退出。
在 cleanup_and_quit 和 kill_process_tree 中加入了 taskkill /F /T 和 psutil 递归强杀，确保退出时彻底清理 Blender 子进程。
用 os._exit(0) 替代了普通的退出，防止 PyQt 线程卡死导致进程残留。

3. 新增“并行任务数”功能
原版是单线程队列（BatchRenderThread），一次只能渲染一个任务。我新增了 RenderWorker 类和 queue.Queue 任务队列，现在支持在控制台选择并行任务数（1~8），显著提升多显卡或多核 CPU 的利用率。

4. 系统监控新增“显存占用（VRAM）”显示
原版只能看显卡利用率（get_gpu_usage）。我将其升级为 get_gpu_info，配合 pynvml 库，现在可以同时显示“GPU利用率”和“显存占用（已用/总量）”，大项目渲染时更加直观。

5. 优化了参数提取的容错与超时机制
在 ParamExtractorThread 中加入了 --factory-startup 参数，防止第三方插件导致参数提取崩溃。
加入了 30 秒超时机制（communicate(timeout=30)），避免某个损坏的 .blend 文件把整个软件卡死。
优化了错误报错的日志输出（双击错误任务弹窗展示详情）。

6. 新增“打开工程”按钮
在任务列表中选中工程后，可以直接通过底部按钮调用 Blender 打开该 .blend 文件，方便快速修改参数，无需手动去文件夹里寻找。

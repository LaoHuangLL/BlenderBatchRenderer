import sys
import time
import os
import json
import subprocess
import tempfile
import copy
import re
import math
import ctypes
import threading
import queue
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QFileDialog, QTextEdit, QSplitter, QGroupBox,
    QGridLayout, QMessageBox, QAbstractItemView, QCheckBox,
    QProgressBar, QDialog, QStyle, QStyledItemDelegate, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QColor, QBrush, QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

THEME_COLORS = {
    "bg_app": "#18181B",
    "bg_panel": "#27272A",
    "bg_input": "#3F3F46",
    "bg_input_hover": "#52525B",
    "text_main": "#F4F4F5",
    "text_muted": "#A1A1AA",
    "border_light": "#3F3F46",
    "border_focus": "#3B82F6",
    "accent": "#3B82F6",
    "accent_hover": "#60A5FA",
    "btn_start": "#10B981",
    "btn_start_hover": "#34D399",
    "btn_stop": "#EF4444",
    "btn_stop_hover": "#F87171",
    "progress_bg": "#3F3F46",
    "progress_chunk": "#10B981",
    "list_wait": "#fff",
    "list_running": "#3B82F6",
    "list_complete": "#10B981",
    "list_failed": "#EF4444",
    "list_stopped": "#71717A",
}

TRANSLATIONS = {
    "zh": {
        "title": "Blender 批量渲染器 Pro 丨 By 舟午YueMoon",
        "blender_group": "Blender 程序路径",
        "set_path": "选择路径",
        "lang_btn": "English",
        "project_list": "任务列表",
        "params_group": "任务参数设置",
        "control_group": "控制台",
        "start": "▶ 开始渲染",
        "stop": "■ 停止渲染",
        "import": "导入工程", "copy": "复制选中", "delete": "删除选中",
        "refresh": "刷新参数", "reset": "重置状态", "clear": "清空列表",
        "open_blend": "打开工程",
        "after": "完成后:", "none": "无", "shutdown": "关机", "sleep": "睡眠", "restart": "重启",
        "warning": "提示",
        "error": "错误",
        "select_task_warn": "请先在列表中选中需要操作的任务！",
        "set_blender_first": "请先设置Blender程序路径！",
        "extraction_error": "参数提取错误",
        "file": "文件",
        "reason": "错误原因",
        "add_file": "添加文件",
        "blender_exe": "Blender可执行文件",
        "output": "输出路径",
        "render_complete_prompt": "渲染完成提示",
        "tasks_completed_tip": "所有任务已完成，将在 {countdown}秒 后执行 {action}",
        "cancel": "取消",
        "execute_now": "立即执行 {action}",
        "scene": "场景:",
        "camera": "相机:",
        "res_x": "分辨率X:",
        "res_y": "分辨率Y:",
        "start_frame": "起始帧:",
        "end_frame": "结束帧:",
        "step_frame": "帧步长:",
        "format": "格式:",
        "output_path": "输出路径:",
        "browse": "浏览",
        "system_usage": "系统占用: --%",
        "total_frames_tip": "总帧数: {total} | 已渲染: {rendered} | 任务数: {count} | 已完成: {completed}",
        "cpu_ram_usage": "CPU: {cpu}% | 内存: {ram}% | GPU: {gpu}% | 显存: {vram}",
        "status_waiting": "等待渲染",
        "status_rendering": "正在渲染",
        "status_completed": "渲染完成",
        "status_stopped": "手动停止",
        "status_failed": "渲染出错",
        "status_loading": "加载中",
        "close_warning": "当前存在渲染任务，请停止渲染后再关闭本软件。",
        "exiting_tip": "正在退出（清理子进程），请稍候…",
        "log_task_start": "开始渲染第 {idx} 个任务，任务名：“{name}”，保存位置：“{path}”",
        "log_frame_done": "完成第 {idx} 任务的第 {frame} 帧，用时 {time_str}",
        "log_missing": "⚠️ 警告：检测到工程中有内容丢失 -> {detail}",
        "log_task_done": "完成渲染：“{name}”，总用时： {time_str}",
        "log_all_done": "全部渲染任务完成，本次共渲染 {task_count} 个任务，共 {frame_count} 帧，总计用时 {time_str}",
        "log_stopped": "渲染被手动停止",
        "clear_log": "清空日志",
        "time_stats": "总耗时: {total} | 当前帧: {current} | 平均帧: {avg} | 预计剩余: {eta}",
        "quit_warning_text": "当前存在渲染任务，是否确认停止渲染并退出软件？",
        "confirm_quit": "确认退出",
        "frame_sample": "当前帧采样: %v / %m",
        "frame_task_prefix": "【任务 {idx}】{text}",
        "total_progress": "总渲染进度: %p%",
        "custom_frames": "自定义帧:",
        "custom_frames_ph": "输入自定义渲染的帧，用英文逗号隔开",
        "custom_frames_err_log": "⚠️ 警告：任务 “{name}” 的自定义帧格式错误，只能包含数字和英文逗号！",
        "custom_frames_err_box": "任务 “{name}” 的自定义帧格式错误！\n请确保只能输入数字，并用英文逗号隔开。\n\n例如：1,5,10",
        "auto_fill": "自动填入缺失帧",
        "clear_cf": "清空",
        "no_output_path": "请先设置输出路径！",
        "no_missing_frames": "当前范围内没有发现缺失的帧！",
        "log_auto_fill": "任务 “{name}” 已自动填入 {count} 个缺失帧。",
        "cpu_limit": "CPU资源分配:",
        "cpu_100": "100% (全速渲染)",
        "cpu_75": "75% (预留给系统)",
        "cpu_50": "50% (边看网页边渲)",
        "cpu_25": "25% (纯后台潜水)",
        "parallel_label": "并行任务数:",
        "indep_process": "每帧渲染完成后自动清空内存（大项目推荐勾选）",
        "indep_process_tt": "适用于物理/SSS等复杂场景：每渲完一帧自动杀进程清空内存，防止越来越慢",
        "frame_sample_tiled": "当前帧进度: Sample: {c_s}/{t_s} | Tiles: {c_t}/{t_t}",
        "denoising": "正在降噪...",
        "log_resume_progress": "检测到 {count} 个已经渲染好的帧，已计入总渲染进度（Blender 会自动跳过这些帧）。",
        "log_scan_failed": "⚠️ 任务 “{name}” 的输出目录里有文件，但没能识别出已渲染的帧（示例文件：{samples}）。该任务进度会从 0 开始，请确认“输出路径”和帧文件命名是否一致。",
        "log_finalize_watchdog": "✅ 渲染已全部完成，但 Blender 进程没有自行退出（可能卡在收尾阶段），已自动结束该进程并继续。",
    },
    "en": {
        "title": "Blender Batch Renderer Pro | By 舟午YueMoon",
        "blender_group": "Where is your Blender?",
        "set_path": "Set Blender Path",
        "lang_btn": "中文",
        "project_list": "Project List",
        "params_group": "Task Parameter Settings",
        "control_group": "Control",
        "start": "▶ Start",
        "stop": "■ Stop",
        "import": "Import", "copy": "Copy Sel", "delete": "Delete Sel",
        "refresh": "Refresh Para", "reset": "Reset Status", "clear": "Clear All",
        "open_blend": "Open Blend",
        "after": "After:", "none": "None", "shutdown": "Shut Down", "sleep": "Sleep", "restart": "Restart",
        "warning": "Warning",
        "error": "Error",
        "select_task_warn": "Please select the task to operate first!",
        "set_blender_first": "Set Blender path first!",
        "extraction_error": "Extraction Error",
        "file": "File",
        "reason": "Reason",
        "add_file": "Add file",
        "blender_exe": "Blender Executable",
        "output": "Output",
        "render_complete_prompt": "Render Completion Prompt",
        "tasks_completed_tip": "Tasks completed. {action} in {countdown}s",
        "cancel": "Cancel",
        "execute_now": "{action} Now",
        "scene": "Scene:",
        "camera": "Camera:",
        "res_x": "Res X:",
        "res_y": "Res Y:",
        "start_frame": "Start:",
        "end_frame": "End:",
        "step_frame": "Step:",
        "format": "Format:",
        "output_path": "Output:",
        "browse": "Browse",
        "system_usage": "System Usage: --%",
        "total_frames_tip": "Total Frames: {total} | Rendered: {rendered} | Tasks: {count} | Completed: {completed}",
        "cpu_ram_usage": "CPU: {cpu}% | RAM: {ram}% | GPU: {gpu}% | VRAM: {vram}",
        "status_waiting": "Waiting",
        "status_rendering": "Rendering",
        "status_completed": "Completed",
        "status_stopped": "Stopped",
        "status_failed": "Failed",
        "status_loading": "Loading",
        "close_warning": "There is an active rendering task. Please stop rendering before closing the software.",
        "exiting_tip": "Exiting (cleaning up processes), please wait…",
        "log_task_start": "Started rendering task: {idx}, Task Name: \"{name}\", Output: \"{path}\"",
        "log_frame_done": "Completed task {idx}, frame {frame}, time taken {time_str}",
        "log_missing": "⚠️ Warning: Missing content detected in project -> {detail}",
        "log_task_done": "Finished rendering: “{name}”，total time:  {time_str}",
        "log_all_done": "All tasks completed. Rendered {task_count} tasks, {frame_count} frames. Total time {time_str}.",
        "log_stopped": "Rendering was manually stopped",
        "clear_log": "Clear Log",
        "time_stats": "Total: {total} | Current: {current} | Average: {avg} | ETA: {eta}",
        "quit_warning_text": "Active rendering task exists. Stop rendering and quit?",
        "confirm_quit": "Confirm Quit",
        "frame_sample": "Frame Sampling: %v / %m",
        "frame_task_prefix": "[Task {idx}] {text}",
        "total_progress": "Total Progress: %p%",
        "custom_frames": "Custom Frames:",
        "custom_frames_ph": "Enter custom frames, separated by commas",
        "custom_frames_err_log": "⚠️ Warning: Task '{name}' custom frames format is invalid! Use only numbers and commas.",
        "custom_frames_err_box": "Task '{name}' has invalid custom frames format!\nPlease use only numbers separated by commas.\n\nExample: 1,5,10",
        "auto_fill": "Auto-Fill Missing",
        "clear_cf": "Clear",
        "no_output_path": "Please set the output path first!",
        "no_missing_frames": "No missing frames found in the current range!",
        "log_auto_fill": "Task '{name}': Auto-filled {count} missing frames.",
        "cpu_limit": "CPU Allocation:",
        "cpu_100": "100% (Full Speed)",
        "cpu_75": "75% (Leave some room)",
        "cpu_50": "50% (Multitasking)",
        "cpu_25": "25% (Background)",
        "parallel_label": "Parallel Tasks:",
        "indep_process": "Per-Frame Independent Rendering",
        "indep_process_tt": "Kills process after each frame to prevent memory leaks in complex scenes.",
        "frame_sample_tiled": "Frame Sample: {c_s}/{t_s} | Tiles: {c_t}/{t_t}",
        "denoising": "Denoising...",
        "log_resume_progress": "Detected {count} already rendered frames, they are counted into the total progress (Blender will skip them).",
        "log_scan_failed": "⚠️ Task \"{name}\" has files in its output folder but no rendered frames were recognized (sample files: {samples}). Its progress starts from 0; please check the output path and the frame file naming.",
        "log_finalize_watchdog": "✅ Render finished, but the Blender process did not exit on its own (it may be stuck while wrapping up). It was terminated automatically, continuing.",
    }
}

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


CONFIG_FILE = "BlenderBatchRenderer_config.json"
SESSION_FILE = "BlenderBatchRenderer_session.json"
SERVER_NAME = "BlenderBatchRenderer_Pro_SingleInstance"
_LOCAL_SERVER = None


def write_config_to_disk(config_data):
    """写配置文件（纯数据，可在任意线程调用）。"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
    except Exception:
        pass


# 子进程（Blender）不显示控制台窗口；同时让它成为新进程组的组长。
# 保留 CREATE_NEW_PROCESS_GROUP 只是因为它是既有的启动参数，停止渲染时不再依赖
# 控制台信号 CTRL_BREAK：实测 Blender 后台模式不处理 SIGBREAK，投递它等于“立即
# 终止”，还要搭上 FreeConsole/AttachConsole 的风险（会干扰本程序自己的控制台），
# 收益为零。现在的停止路径是：限时等待 -> psutil 递归结束整棵进程树。
BLENDER_CREATE_FLAGS = (
    getattr(subprocess, "CREATE_NO_WINDOW", 0)
    | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
)

_SESSION_LOCK = threading.Lock()
_TRACK_LOCK = threading.Lock()
_TRACKED_PROCS = set()    # 本程序启动的渲染 / 参数提取子进程，退出时统一清理
_DETACHED_PROCS = set()   # 用户主动“打开工程”启动的 Blender，退出时不动它


# ---------------------------------------------------------------------------
# 帧号 / 已渲染帧统计
# ---------------------------------------------------------------------------
def _custom_frame_numbers(task):
    """解析自定义帧；没有配置或全部非法时返回 None。"""
    cf = str(getattr(task, 'custom_frames', '') or '').strip()
    if not cf:
        return None
    nums = []
    for part in cf.split(','):
        part = part.strip()
        if part.isdigit():
            nums.append(int(part))
    return nums or None


def _task_frame_range(task):
    """按起止帧/步长算出帧范围（range 对象，取长度是 O(1)）。"""
    try:
        start = int(task.frame_start)
        end = int(task.frame_end)
        step = int(task.frame_step)
    except (TypeError, ValueError):
        return None
    if step <= 0:
        step = 1
    if end < start:
        return None
    return range(start, end + 1, step)


def get_task_frame_numbers(task):
    """返回任务需要渲染的帧号列表（自定义帧优先）。
    进度统计、ETA、磁盘扫描都用它，保证口径一致。"""
    if task is None:
        return []
    nums = _custom_frame_numbers(task)
    if nums is not None:
        return list(nums)
    frame_range = _task_frame_range(task)
    return list(frame_range) if frame_range is not None else []


def count_task_frames(task):
    """任务总帧数。不构造帧号列表，供调用频繁的统计逻辑使用。"""
    if task is None:
        return 0
    nums = _custom_frame_numbers(task)
    if nums is not None:
        return len(nums)
    frame_range = _task_frame_range(task)
    return len(frame_range) if frame_range is not None else 0


def resolve_output_scan(task):
    """解析输出路径，返回 (要扫描的目录, 文件名前缀)。

    - 输出路径本身是目录（例如 E:\\out2\\镜头\\）：Blender 在里面生成 0001.png，前缀为空；
    - 输出路径是文件名前缀（例如 E:\\out2\\frame_）：Blender 生成 frame_0001.png。
    路径不存在或为空时返回 None。
    """
    out_path = str(getattr(task, 'output_path', '') or '').strip().strip('"')
    if not out_path:
        return None
    try:
        norm_path = os.path.normpath(out_path)
        if os.path.isdir(norm_path):
            return norm_path, ""
        return os.path.dirname(norm_path), os.path.basename(norm_path)
    except Exception:
        return None


def _scan_dir_frame_numbers(scan_dir, base_name, expected_set):
    """扫描目录，返回落在任务帧范围内的帧号集合。

    优先按「文件名以数字开头」识别（0001.png）；一个都没识别到时，
    才退回到带前缀的命名（镜头_0001.png），并只采用出现次数最多的那个前缀，
    避免把同目录里其它任务的文件也算进来。
    """
    numeric = set()
    loose = {}  # 前缀 -> 帧号集合
    try:
        with os.scandir(scan_dir) as entries:
            for entry in entries:
                name = entry.name
                if base_name:
                    if not name.startswith(base_name):
                        continue
                    suffix = name[len(base_name):]
                    match = re.match(r'^(\d+)', suffix)
                    if match:
                        num = int(match.group(1))
                        if num in expected_set:
                            numeric.add(num)
                    continue

                match = re.match(r'^(\d+)', name)
                if match:
                    num = int(match.group(1))
                    if num in expected_set:
                        numeric.add(num)
                    continue

                tail = re.search(r'^(.*?)(\d+)\.[^.\\/]+$', name)
                if tail:
                    num = int(tail.group(2))
                    if num in expected_set:
                        loose.setdefault(tail.group(1), set()).add(num)
    except Exception:
        return numeric

    if numeric or not loose:
        return numeric
    return max(loose.values(), key=len)


def scan_existing_frames(task):
    """返回该任务范围内「磁盘上已经存在」的帧号集合。

    这些帧 Blender 会跳过，必须计入“总渲染进度”，进度才不会归零。
    """
    expected = get_task_frame_numbers(task)
    if not expected:
        return set()
    target = resolve_output_scan(task)
    if target is None:
        return set()
    scan_dir, base_name = target
    if not scan_dir or not os.path.isdir(scan_dir):
        return set()
    return _scan_dir_frame_numbers(scan_dir, base_name, set(expected))


def inspect_output_dir(task, sample_limit=3):
    """返回 (输出目录里的条目数, 前几个文件名)。

    仅用于诊断：目录里明明有文件却识别不出帧时，把样例文件名打到日志里，
    方便判断是“输出路径不对”还是“文件命名不匹配”。
    """
    target = resolve_output_scan(task)
    if target is None:
        return 0, []
    scan_dir = target[0]
    if not scan_dir or not os.path.isdir(scan_dir):
        return 0, []
    count, samples = 0, []
    try:
        with os.scandir(scan_dir) as entries:
            for entry in entries:
                count += 1
                if len(samples) < sample_limit:
                    samples.append(entry.name)
    except Exception:
        return count, samples
    return count, samples


def count_output_dir_files(task):
    """输出目录里有多少个条目（诊断用）。"""
    return inspect_output_dir(task)[0]


def task_frames_present_on_disk(task):
    """任务范围内的帧是否都已经在磁盘上了。

    看门狗收尾前的最后一道确认：只有“该渲的帧全都在盘上”才敢结束迟迟不退出的进程，
    避免误杀一个正在慢慢渲染（只是暂时没有输出）的 Blender。
    """
    expected = get_task_frame_numbers(task)
    if not expected:
        return False
    return len(scan_existing_frames(task)) >= len(expected)


# ---------------------------------------------------------------------------
# 子进程管理：登记 / 优雅停止 / 强制清理
# ---------------------------------------------------------------------------
def track_process(proc, detached=False):
    if proc is None:
        return
    with _TRACK_LOCK:
        (_DETACHED_PROCS if detached else _TRACKED_PROCS).add(proc)


def untrack_process(proc):
    if proc is None:
        return
    with _TRACK_LOCK:
        _TRACKED_PROCS.discard(proc)
        _DETACHED_PROCS.discard(proc)


def _tracked_processes():
    with _TRACK_LOCK:
        return list(_TRACKED_PROCS)


def _process_exited(proc):
    if proc is None:
        return True
    try:
        return proc.poll() is not None
    except Exception:
        return True


def _wait_process_exit(proc, timeout, interval=0.05):
    """在 timeout 秒内轮询等待进程退出，返回是否已退出（绝不无限等待）。"""
    deadline = time.time() + max(0.0, float(timeout))
    while True:
        if _process_exited(proc):
            return True
        if time.time() >= deadline:
            return False
        time.sleep(interval)


def _winapi(dll, name, argtypes, restype):
    """给 Win32 函数声明正确的签名。

    ctypes 不声明 argtypes/restype 时会按 C 的 int 处理：64 位句柄会被截断成
    32 位，调用直接失败（返回 0）却不报错。这类「静默失败」在退出路径上是致命的
    —— 你以为是强杀了，其实什么也没做。
    """
    try:
        func = getattr(dll, name)
        func.argtypes = argtypes
        func.restype = restype
        return func
    except Exception:
        return None


def _pid_alive(pid):
    if not pid or pid <= 0:
        return False
    if HAS_PSUTIL:
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False
    try:
        kernel32 = ctypes.windll.kernel32
        # 这里同样必须声明签名：否则 64 位句柄会被截断，判断结果不可信
        open_process = _winapi(kernel32, "OpenProcess",
                               [ctypes.c_uint, ctypes.c_int, ctypes.c_uint], ctypes.c_void_p)
        close_handle = _winapi(kernel32, "CloseHandle", [ctypes.c_void_p], ctypes.c_bool)
        if open_process is None or close_handle is None:
            return False
        handle = open_process(0x1000, False, int(pid))   # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        close_handle(handle)
        return True
    except Exception:
        return False


_KERNEL32 = None
try:
    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _KERNEL32.PeekNamedPipe.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p,
    ]
    _KERNEL32.PeekNamedPipe.restype = ctypes.c_bool
except Exception:
    _KERNEL32 = None


def _pipe_probe_handle(stream):
    """取管道的系统句柄；取不到返回 None。"""
    try:
        import msvcrt
        handle = msvcrt.get_osfhandle(stream.fileno())
        if handle and handle != -1:
            return int(handle)
    except Exception:
        pass
    return None


class _PipePoller:
    """非阻塞读取子进程的 stdout 管道（Windows：PeekNamedPipe 轮询）。

    以前的写法是「单开一个线程 read(1) 死等 + 退出时 CancelIoEx 再 close 那个句柄」，
    这里有两个真实隐患：

      1) 同步管道（Python 的 open/pipe 句柄不是 OVERLAPPED 打开的）上的 ReadFile
         卡住以后，CancelIoEx 是取消不掉的 —— 它只对异步 I/O 有效。于是那个读线程
         永远回不来。
      2) 在另一个线程里 close 一个正在被读的管道句柄，属于未定义行为，可能直接
         卡在句柄锁上。

    只要进程里有一个线程永远回不来，本程序在退出时就会变成「已决定终止、但终止
    不完」的悬挂状态，此时再对它 TerminateProcess 就是「拒绝访问」。
    所以这里改成纯粹的非阻塞轮询：不需要额外线程，退出时也不存在跨线程关句柄。
    """

    def __init__(self, stream, read_size=65536):
        self._stream = stream
        self._handle = None
        self._queue = None
        self._thread = None
        self._read_size = read_size
        self._eof = False
        if stream is not None:
            self._handle = _pipe_probe_handle(stream)
            if self._handle is None or _KERNEL32 is None:
                self._start_reader_thread()

    # -- 退路：万一 PeekNamedPipe 用不了，退回「后台线程 + 队列」，对外接口一致 --
    def _start_reader_thread(self):
        self._handle = None
        self._queue = queue.Queue()

        def _reader():
            while True:
                try:
                    chunk = self._stream.read(4096)
                except Exception:
                    chunk = b""
                if not chunk:
                    self._queue.put(None)
                    return
                self._queue.put(chunk)

        self._thread = threading.Thread(target=_reader, daemon=True)
        self._thread.start()

    def read(self):
        """返回 bytes；b"" 表示对端已关闭（EOF）；None 表示暂时没有数据。"""
        if self._eof:
            return b""
        if self._queue is not None:
            try:
                chunk = self._queue.get_nowait()
            except queue.Empty:
                return None
            if chunk is None:
                self._eof = True
            return chunk
        try:
            pending = ctypes.c_ulong(0)
            ok = _KERNEL32.PeekNamedPipe(
                ctypes.c_void_p(self._handle), None, 0, None,
                ctypes.byref(pending), None,
            )
            if not ok:
                self._eof = True          # ERROR_BROKEN_PIPE 等：对端已关闭
                return b""
            size = int(pending.value)
            if size <= 0:
                return None
            data = os.read(self._stream.fileno(), min(size, self._read_size))
            if not data:
                self._eof = True
            return data
        except Exception:
            self._eof = True
            return b""

    def close(self):
        """关闭管道句柄。读线程还活着时绝不动这个句柄（不跨线程关正在读的句柄）。"""
        if self._thread is not None:
            try:
                self._thread.join(0.5)
            except Exception:
                pass
            if self._thread.is_alive():
                # 读线程还卡着：句柄交给它，进程退出时由系统回收，绝不在这里强行 close
                self._stream = None
        stream = self._stream
        self._stream = None
        if stream is not None:
            try:
                stream.close()
            except Exception:
                pass


def release_process_handles(proc, timeout=1.0):
    """结束残留的子进程（不碰 stdio）。

    管道句柄一律交给读它的那一方自己关闭：跨线程关一个正在被读的句柄，
    有可能让本程序卡在句柄锁上 —— 这类卡死是「关软件时拒绝访问」的成因之一。
    """
    if proc is None:
        return
    try:
        if proc.poll() is None:
            proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=timeout)
    except Exception:
        pass


# 结束子进程的总时间预算（秒）。关软件时宁可留下日志硬退，也绝不允许无限等。
DEFAULT_KILL_BUDGET = 4.0


def _alive_pids(procs):
    """这批 Popen 里还有谁活着（返回 PID 列表）。"""
    alive = []
    for proc in procs or []:
        if proc is None or _process_exited(proc):
            continue
        pid = getattr(proc, 'pid', None)
        if pid:
            alive.append(int(pid))
    return alive


def kill_processes(procs, deadline=None, include_children=True):
    """限时、批量地结束一批子进程（连同它们的子树）。

    和以前「逐个 taskkill /F /T + 逐个 wait」的区别：
      * 不再额外 spawn 一个 taskkill 进程（关软件时再启动新进程本身就是风险源）；
      * psutil 一次处理整棵子树，所有进程共用同一个截止时间，不会 N 个进程各等 4 秒；
      * 返回「被系统拒绝访问」的 PID，用于在退出日志里说明真相，
        而不是像原来那样把 Access is denied 悄悄吞掉。
    """
    procs = [p for p in (procs or []) if p is not None]
    if not procs:
        return []
    if deadline is None:
        deadline = time.time() + DEFAULT_KILL_BUDGET
    denied = []
    targets = []

    if HAS_PSUTIL:
        for proc in procs:
            pid = getattr(proc, 'pid', None)
            if not pid:
                continue
            try:
                parent = psutil.Process(pid)
            except Exception:
                continue  # 进程已经不在了，没什么可杀的
            tree = []
            if include_children:
                try:
                    tree = parent.children(recursive=True)
                except Exception:
                    tree = []
            tree.append(parent)
            for item in tree:
                if item in targets:
                    continue
                targets.append(item)
                try:
                    item.kill()
                except psutil.NoSuchProcess:
                    pass
                except psutil.AccessDenied:
                    # 进程已经进入系统级「终止中」状态时，连 TerminateProcess 都会被拒。
                    denied.append(item.pid)
                except Exception:
                    pass
    else:
        # 没有 psutil 时的退路：一次 taskkill 打完，带超时
        cmd = ["taskkill", "/F", "/T"]
        for proc in procs:
            pid = getattr(proc, 'pid', None)
            if pid:
                cmd.extend(["/PID", str(pid)])
        if len(cmd) > 3:
            try:
                subprocess.run(
                    cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, timeout=2.0,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except Exception:
                pass

    # Popen 对象自己再兜一次（psutil 里没登到、或者 kill 被拒的场景）
    for proc in procs:
        try:
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pid = getattr(proc, 'pid', None)
            if pid:
                denied.append(int(pid))

    # 统一等一次，上限是整个 deadline，不逐个累加
    if targets:
        try:
            psutil.wait_procs(targets, timeout=max(0.0, deadline - time.time()))
        except Exception:
            pass
    for proc in procs:
        left = max(0.0, deadline - time.time())
        try:
            proc.wait(timeout=min(1.0, left) if left > 0 else 0.0)
        except Exception:
            pass
        untrack_process(proc)
    return denied


def terminate_process_tree(proc, grace=1.2, force_timeout=4.0):
    """终止子进程及其整棵子树，返回 True 表示已确认退出。

    顺序：可选的自然退出等待 -> psutil 递归强杀（含 Popen.kill 兜底）-> 复查。
    每一步都带时限，绝不死等，避免关软件时把自己也拖成卡死的进程。

    注意：这里不再投递 CTRL_BREAK / 也不再折腾 FreeConsole + AttachConsole。
    Blender 后台模式并不处理 SIGBREAK（项目里原本的注释也承认这一点），
    那套 console 操作唯一确定的效果是把本程序自己的控制台 detach 掉，
    属于「有副作用、没收益」的高风险动作，已经删掉。
    """
    if proc is None:
        return True
    pid = getattr(proc, 'pid', None)
    if not pid:
        return True

    if _process_exited(proc):
        release_process_handles(proc)
        untrack_process(proc)
        return True

    if grace > 0 and _wait_process_exit(proc, grace):
        release_process_handles(proc)
        untrack_process(proc)
        return True

    kill_processes([proc], deadline=time.time() + max(0.5, float(force_timeout)))
    release_process_handles(proc)
    return _process_exited(proc)


def terminate_process_tree_by_pid(pid, force_timeout=4.0):
    """按 PID 结束整棵进程树（只剩 PID、没有 Popen 对象的场景）。"""
    if not _pid_alive(pid):
        return True
    deadline = time.time() + max(0.5, float(force_timeout))
    if HAS_PSUTIL:
        try:
            parent = psutil.Process(int(pid))
        except Exception:
            return True
        tree = []
        try:
            tree = parent.children(recursive=True)
        except Exception:
            tree = []
        tree.append(parent)
        for item in tree:
            try:
                item.kill()
            except Exception:
                pass
        try:
            psutil.wait_procs(tree, timeout=max(0.0, deadline - time.time()))
        except Exception:
            pass
    else:
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=force_timeout,
            )
        except Exception:
            pass
    return not _pid_alive(pid)


def stop_processes(procs, grace=0.0, force_timeout=4.0):
    """限时停止一批子进程，返回被系统拒绝访问 / 仍存活可疑的 PID 列表。"""
    procs = [p for p in (procs or []) if p is not None and not _process_exited(p)]
    if not procs:
        return []
    deadline = time.time() + max(0.2, float(force_timeout))
    if grace > 0:
        # 先给一点自然退出的时间（大多数情况这里就走了），再统一强杀
        grace_deadline = min(deadline, time.time() + float(grace))
        while time.time() < grace_deadline and any(not _process_exited(p) for p in procs):
            time.sleep(0.05)
    return kill_processes(procs, deadline=deadline)


def terminate_all_tracked_processes(grace=0.0, force_timeout=4.0):
    return stop_processes(_tracked_processes(), grace=grace, force_timeout=force_timeout)


def sweep_orphan_children(force_timeout=3.0):
    """兜底：清理仍挂在名下的 Blender 子进程（跳过用户主动打开的 Blender）。

    返回仍然活着的 PID 列表，供退出日志说明「还有东西没死」。
    """
    if not HAS_PSUTIL:
        return []
    protected = set()
    with _TRACK_LOCK:
        for proc in _DETACHED_PROCS:
            pid = getattr(proc, 'pid', None)
            if pid:
                protected.add(pid)
    try:
        children = psutil.Process(os.getpid()).children(recursive=True)
    except Exception:
        return []
    victims = []
    for child in children:
        if child.pid in protected:
            continue
        try:
            name = child.name().lower()
        except Exception:
            name = ""
        if "blender" in name:
            victims.append(child)
    for victim in victims:
        try:
            victim.kill()
        except Exception:
            pass
    survivors = []
    if victims:
        try:
            _, alive = psutil.wait_procs(victims, timeout=max(0.5, float(force_timeout)))
            survivors = [p.pid for p in alive]
        except Exception:
            pass
    return survivors


EXIT_LOG_FILE = "BlenderBatchRenderer_exit.log"
_EXIT_LOG_LOCK = threading.Lock()

# 退出流程的两个硬指标：
#   SHUTDOWN_KILL_BUDGET —— 后台线程清理子进程的预算
#   SHUTDOWN_HARD_LIMIT  —— 无论如何都必须结束本进程的硬上限
# 几个预算相加（0.3 + 2.5 + 1.2 + 1.2 + 1.2 ≈ 6.4s）要明显小于硬上限。
SHUTDOWN_KILL_BUDGET = 2.5
SHUTDOWN_HARD_LIMIT = 9.0


def _exit_log_paths():
    """退出日志的候选路径（同时写多处，事后总能找到其中一个）。

    当前目录不一定是程序所在目录：PyInstaller onedir 打包后从资源管理器双击
    启动时 CWD 可能是任意位置，所以外加 exe 所在目录和 %TEMP%。
    """
    paths = [os.path.abspath(EXIT_LOG_FILE)]
    try:
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        cand = os.path.join(app_dir, EXIT_LOG_FILE)
        if cand not in paths:
            paths.append(cand)
    except Exception:
        pass
    try:
        tmp = os.environ.get("TEMP") or os.environ.get("TMP")
        if tmp:
            cand = os.path.join(tmp, EXIT_LOG_FILE)
            if cand not in paths:
                paths.append(cand)
    except Exception:
        pass
    return paths


def log_exit(message):
    """退出流程的极简日志（带时间戳，同时写当前目录 / 程序目录 / TEMP）。

    这类「关闭时卡住 / 拒绝访问」的问题和环境强相关，事后没有现场就只能靠猜。
    留一条带时间戳的记录，下次直接能看出是哪一步慢、哪个 PID 被拒绝访问。
    写文件不经过显卡驱动，因此即使某个线程卡在驱动里，这些记录照样能落盘。
    """
    try:
        line = "[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), message)
        with _EXIT_LOG_LOCK:
            for path in _exit_log_paths():
                try:
                    if os.path.exists(path) and os.path.getsize(path) > 256 * 1024:
                        os.remove(path)
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(line)
                except Exception:
                    pass
    except Exception:
        pass


def _terminate_self(code):
    """用 TerminateProcess 结束自己，返回 (是否成功, 失败时的 Win32 错误码)。

    错误码非常关键：
      5  = ERROR_ACCESS_DENIED   -> 本进程已经在「终止中」，外部强杀同样会得到它
      6  = ERROR_INVALID_HANDLE  -> 签名/句柄问题（旧代码就是悄悄踩在这个上）
      其它 -> 原样记进退出日志
    """
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_current = _winapi(kernel32, "GetCurrentProcess", [], ctypes.c_void_p)
        terminate = _winapi(kernel32, "TerminateProcess",
                            [ctypes.c_void_p, ctypes.c_uint], ctypes.c_bool)
        if get_current is None or terminate is None:
            return False, -1
        if terminate(get_current(), int(code)):
            return True, 0
        return False, ctypes.get_last_error()
    except Exception as exc:
        return False, -2


def force_exit(code=0, why=""):
    """立即结束本进程。

    优先用 TerminateProcess：它跳过 ExitProcess 的逐 DLL 卸载通知
    （Qt、显卡驱动都在 DllMain 里做收尾，那一步是最容易死锁的地方），
    而死锁的后果就是进程卡在「终止中」状态 —— 之后连任务管理器的「结束任务」
    都会报「拒绝访问」。

    注意这里是**真的**调用了 TerminateProcess（带正确签名）。旧代码没有声明
    argtypes，GetCurrentProcess() 返回的伪句柄被截断成 32 位，TerminateProcess
    实际返回失败（错误码 6/无效句柄）却没有检查，于是每次都悄悄退化成了
    os._exit() —— 也就是回到了它本想避开的 ExitProcess 路径。已实测确认并修好。

    另外：正常路径下一定从 GUI 主线程调用（见 _final_exit_if_ready）。
    ExitProcess 从非主线程调用会去抢加载器锁，而主线程此刻正待在 Qt 事件循环里，
    那是一个真实的死锁点。

    说明 2：如果真有线程卡在显卡驱动的内核态等待里，任何用户态手段都结束不了它
    （Windows 的限制，只能重启）。所以这里的职责是：第一不要让自己成为那种进程，
    第二万一变成了，也要在退出日志里留下证据 —— 就是下面那行日志。
    """
    ok, err = _terminate_self(code)
    # 能执行到这一行，说明 TerminateProcess 并没有结束本进程 —— 这本身就是最重要的证据
    log_exit(
        "TerminateProcess(%r) 返回 %r / 错误码 %r，但本进程仍然存活（调用点：%s）；"
        "存活线程：%s。"
        "错误码 5=ERROR_ACCESS_DENIED 表示本进程已在「终止中」，"
        "错误码其它值或仍存活通常意味着有线程卡在内核态（多半是显卡驱动）。"
        % (code, ok, err, why or "未知",
           ", ".join(sorted({t.name for t in threading.enumerate()}))))
    os._exit(code)


# 最后一帧渲完之后，Blender 偶尔不会自行退出（卡在收尾 / 显卡驱动阶段），
# 这时不再无限等待，超过这个时间就主动结束它，让批次能正常收尾。
RENDER_FINALIZE_GRACE = 45.0


def reached_last_frame(frame_label, last_frame):
    """日志里的帧号是否已经到达任务的最后一帧。"""
    if last_frame is None:
        return False
    try:
        return int(str(frame_label).strip()) >= int(last_frame)
    except (TypeError, ValueError):
        return False


def should_finalize_lingering_process(proc, finished_at, grace=RENDER_FINALIZE_GRACE, now=None):
    """渲染已经结束、但进程迟迟不退出时，是否该主动结束它。"""
    if proc is None or finished_at is None:
        return False
    if _process_exited(proc):
        return False
    if now is None:
        now = time.time()
    return (now - finished_at) >= grace


class MyDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


class RenderTask:
    def __init__(self, blend_path):
        self.blend_path = blend_path
        self.name = os.path.basename(blend_path)
        self.scene_name = ""
        self.camera_name = ""
        self.frame_start = 1
        self.frame_end = 250
        self.frame_step = 1
        self.resolution_x = 1920
        self.resolution_y = 1080
        self.output_path = ""
        self.output_format = "PNG"
        self.custom_frames = ""
        self.independent_process = False
        self.status = "Waiting"
        self.load_status = "Loading"
        self.error_msg = ""
        self.scenes_list = []
        self.cameras_list = []
        self.after_render_action = "None"
        self.rendered_frames = 0
        # 已渲染帧号集合：既有磁盘上已存在（Blender 会跳过）的帧，
        # 也有本次新渲出来的帧，用来自动去重，保证进度只增不减、不会重复计算。
        self.rendered_frame_set = set()
        # 计时（只用于运行期统计，不写进会话文件）：
        # 并行渲染时多个任务同时上报帧，必须按任务各算各的，否则会互相串台。
        self.rendering_started_at = 0.0   # 本任务本次开始渲染的时间
        self.last_frame_time = 0.0        # 本任务上一帧完成的时间
        self.frame_time_total = 0.0       # 本任务累计帧耗时
        self.frame_time_count = 0         # 本任务计时过的帧数
        self.scene_data = {}

    def note_frame_rendered(self, now=None):
        """记录本任务完成了一帧，返回这一帧的耗时（秒）。"""
        now = time.time() if now is None else now
        # 时间戳为 0 表示“还没记录过”，这里显式判断，不用真值判断（0.0 会被当成假）
        if self.last_frame_time > 0:
            base = self.last_frame_time
        elif self.rendering_started_at > 0:
            base = self.rendering_started_at
        else:
            base = now
        cost = max(0.0, now - base)
        self.last_frame_time = now
        self.frame_time_total += cost
        self.frame_time_count += 1
        return cost

    def average_frame_time(self):
        """本任务的平均单帧耗时（秒），还没测到返回 0。"""
        if self.frame_time_count <= 0:
            return 0.0
        return self.frame_time_total / self.frame_time_count

    def seconds_since_last_frame(self, now=None):
        """本任务距离上一帧完成过去了多久（用于显示“当前帧”）"""
        if self.last_frame_time <= 0:
            return 0.0
        now = time.time() if now is None else now
        return max(0.0, now - self.last_frame_time)

    def reset_timing(self, now=None):
        now = time.time() if now is None else now
        self.rendering_started_at = now
        self.last_frame_time = 0.0
        self.frame_time_total = 0.0
        self.frame_time_count = 0

    def set_rendered_frames(self, frames):
        """用一批帧号重置进度（例如开始渲染前扫描磁盘得到的结果）。"""
        nums = set()
        for f in frames or []:
            try:
                nums.add(int(f))
            except (TypeError, ValueError):
                continue
        self.rendered_frame_set = nums
        self.rendered_frames = len(nums)

    def _pick_free_frame_number(self):
        """找一个还没被计入进度的任务帧号（日志解析不出帧号时用）。"""
        for f in get_task_frame_numbers(self):
            if f not in self.rendered_frame_set:
                return f
        return None

    def mark_frame_done(self, frame_num=None):
        """记录一帧完成。已统计过的帧不会重复计数（Blender 重渲同帧时保持进度不变）。"""
        num = None
        if frame_num is not None:
            try:
                num = int(str(frame_num).strip())
            except (TypeError, ValueError):
                num = None
        if num is None:
            num = self._pick_free_frame_number()
            if num is None:
                return False
        if num in self.rendered_frame_set:
            return False
        self.rendered_frame_set.add(num)
        self.rendered_frames = len(self.rendered_frame_set)
        return True

    def to_dict(self):
        return {
            "blend_path": self.blend_path,
            "name": self.name,
            "scene_name": self.scene_name,
            "camera_name": self.camera_name,
            "frame_start": self.frame_start,
            "frame_end": self.frame_end,
            "frame_step": self.frame_step,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "output_path": self.output_path,
            "output_format": self.output_format,
            "status": self.status,
            "load_status": self.load_status,
            "error_msg": self.error_msg,
            "scenes_list": self.scenes_list,
            "cameras_list": self.cameras_list,
            "after_render_action": self.after_render_action,
            "rendered_frames": self.rendered_frames,
            "rendered_frame_set": sorted(self.rendered_frame_set),
            "scene_data": getattr(self, 'scene_data', {}),
            "custom_frames": getattr(self, 'custom_frames', ''),
            "independent_process": getattr(self, 'independent_process', False),
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(data.get("blend_path", ""))
        for k, v in data.items():
            if k in ("rendered_frame_set", "rendered_frames"):
                continue  # 进度相关字段统一在下面处理，保证计数与帧集合一致
            if hasattr(t, k) or k == "scene_data":
                setattr(t, k, v)
        frames = data.get("rendered_frame_set")
        if frames:
            t.set_rendered_frames(frames)
        else:
            # 兼容旧版本会话文件：只有已渲染计数、没有帧集合
            try:
                legacy = int(data.get("rendered_frames", 0) or 0)
            except (TypeError, ValueError):
                legacy = 0
            if legacy > 0:
                t.set_rendered_frames(get_task_frame_numbers(t)[:legacy])
            else:
                t.set_rendered_frames(())
        return t


class ParamExtractorThread(QThread):
    task_finished = pyqtSignal(object)

    def __init__(self, blender_path, task):
        super().__init__()
        self.blender_path = blender_path
        self.task = task
        self.proc = None

    def run(self):
        json_p = os.path.join(tempfile.gettempdir(), f"render_info_{id(self.task)}.json")

        script = f"""
import bpy, json, sys, traceback
try:
    active_scene = bpy.context.scene
    if active_scene is None and len(bpy.data.scenes) > 0:
        active_scene = bpy.data.scenes[0]

    d = {{"active": active_scene.name if active_scene else "", "scenes": {{}}}}
    for s in bpy.data.scenes:
        d["scenes"][s.name] = {{
            "cl": [o.name for o in s.objects if o.type=='CAMERA'],
            "cc": s.camera.name if s.camera else "",
            "fs": s.frame_start, "fe": s.frame_end, "st": s.frame_step,
            "rx": s.render.resolution_x, "ry": s.render.resolution_y,
            "out": s.render.filepath, "fm": s.render.image_settings.file_format
        }}
    with open(r"{json_p}", 'w', encoding='utf-8') as f:
        json.dump(d, f)
    print("EXTRACT_OK")
except Exception as e:
    print("EXTRACT_ERROR:", e)
    traceback.print_exc()
    sys.exit(1)
"""

        ts = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script)
                ts = f.name

            self.proc = subprocess.Popen(
                [self.blender_path, "--factory-startup", "-b", self.task.blend_path, "-P", ts],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=BLENDER_CREATE_FLAGS,
                encoding='utf-8', errors='replace'
            )
            track_process(self.proc)
            try:
                stdout_data, _ = self.proc.communicate(timeout=30)
                rc = self.proc.returncode
            except subprocess.TimeoutExpired:
                proc = self.proc
                terminate_process_tree(proc, grace=0.8)
                # communicate() 超时后，它内部负责读管道的线程还活着。
                # 必须再 communicate 一次把这些线程收掉（顺带关闭管道），
                # 否则后面任何对 stdout 的操作都会变成跨线程关句柄 —— 可能卡死。
                try:
                    proc.communicate(timeout=1.0)
                except Exception:
                    pass
                self.proc = None
                self.task.load_status = "Failed"
                self.task.error_msg = "参数提取超时 (30s)"
                self.task_finished.emit(self.task)
                return
            finally:
                if self.proc is not None:
                    untrack_process(self.proc)
                    release_process_handles(self.proc)
                self.proc = None

            if rc != 0 or not os.path.exists(json_p):
                self.task.load_status = "Failed"
                self.task.error_msg = (
                    f"Blender 退出码: {rc}\n\n"
                    f"--- STDOUT ---\n{(stdout_data or '')[-2000:]}\n"
                )
                self.task_finished.emit(self.task)
                return

            if os.path.exists(json_p):
                with open(json_p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                self.task.scene_data = d.get('scenes', {})
                self.task.scenes_list = list(self.task.scene_data.keys())
                self.task.scene_name = d.get('active', "")
                if self.task.scene_name in self.task.scene_data:
                    sd = self.task.scene_data[self.task.scene_name]
                    self.task.cameras_list = sd.get('cl', [])
                    self.task.camera_name = sd.get('cc', "")
                    self.task.frame_start = sd.get('fs', 1)
                    self.task.frame_end = sd.get('fe', 250)
                    self.task.frame_step = sd.get('st', 1)
                    self.task.resolution_x = sd.get('rx', 1920)
                    self.task.resolution_y = sd.get('ry', 1080)
                    self.task.output_path = sd.get('out', "")
                    self.task.output_format = sd.get('fm', "PNG")
                self.task.load_status = "Success"
            else:
                self.task.load_status = "Failed"
                self.task.error_msg = "Blender did not output parameter JSON."
        except Exception as e:
            self.task.load_status = "Failed"
            self.task.error_msg = str(e)
        finally:
            if ts and os.path.exists(ts):
                try: os.remove(ts)
                except Exception: pass
            if os.path.exists(json_p):
                try: os.remove(json_p)
                except Exception: pass
            self.task_finished.emit(self.task)

    def stop(self):
        try:
            if self.proc and self.proc.poll() is None:
                terminate_process_tree(self.proc, grace=0.0)
        except Exception:
            pass


class RenderWorker(QThread):
    """单个 worker：反复从 task_queue 取任务执行，队列空则退出。"""
    status_updated = pyqtSignal(object, str)
    log_updated = pyqtSignal(str)
    frame_done = pyqtSignal(object, str)
    sample_updated = pyqtSignal(object, int, int, str)   # (任务, 当前, 总数, 标识)
    worker_finished = pyqtSignal()
    notice = pyqtSignal(str)   # 需要写进界面日志的提示（传翻译键）

    def __init__(self, task_queue, blender_path):
        super().__init__()
        self.task_queue = task_queue
        self.blender_path = blender_path
        self.is_running = True
        self.current_process = None
        self.current_rendering_task = None
        self.cpu_pct = 1.0

    def run(self):
        while self.is_running:
            try:
                task = self.task_queue.get_nowait()
            except queue.Empty:
                break

            if task.status in ["Completed", "Stopped", "Failed"] or task.load_status != "Success":
                continue

            self.current_rendering_task = task
            self.render_single_task(task)
            self.current_rendering_task = None

        self.worker_finished.emit()

    def render_single_task(self, task):
        temp_script = None
        poller = None
        try:
            # 注意：这里不能把 rendered_frames 归零。
            # 上一次停止渲染前已经落盘的帧（Blender 这次会跳过）必须保留在进度里，
            # 否则“总渲染进度”会在重新开始时回到 0。
            self.status_updated.emit(task, "Rendering")
            safe_out = task.output_path.replace("\\", "/")

            script_content = f"""
import bpy
try:
    scene = bpy.context.scene
    if "{task.camera_name}" in bpy.data.objects:
        scene.camera = bpy.data.objects["{task.camera_name}"]
    scene.frame_start = {task.frame_start}
    scene.frame_end = {task.frame_end}
    scene.frame_step = {task.frame_step}
    scene.render.resolution_x = {task.resolution_x}
    scene.render.resolution_y = {task.resolution_y}
    scene.render.resolution_percentage = 100
    scene.render.filepath = r"{safe_out}"
    scene.render.image_settings.file_format = "{task.output_format}"
except Exception as e:
    print(f"RENDER_ERROR: {{e}}")
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script_content)
                temp_script = f.name

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            cf = getattr(task, 'custom_frames', '').strip()
            if cf:
                frame_list = [f.strip() for f in cf.split(',') if f.strip().isdigit()]
            else:
                frame_list = [str(f) for f in range(task.frame_start, task.frame_end + 1, task.frame_step)]

            is_indep = getattr(task, 'independent_process', False)

            process_args_list = []
            if is_indep:
                for f_val in frame_list:
                    args = [self.blender_path, "-b", task.blend_path]
                    if task.scene_name:
                        args.extend(["-S", task.scene_name])
                    args.extend(["-P", temp_script, "-f", f_val])
                    process_args_list.append(args)
                # 独立进程模式：每个进程只负责一帧
                process_last_frames = [int(f) for f in frame_list]
            else:
                args = [self.blender_path, "-b", task.blend_path]
                if task.scene_name:
                    args.extend(["-S", task.scene_name])
                args.extend(["-P", temp_script])
                if cf:
                    for f_val in frame_list:
                        args.extend(["-f", f_val])
                else:
                    args.append("-a")
                process_args_list.append(args)
                process_last_frames = [max((int(f) for f in frame_list), default=None)]

            for args, process_last_frame in zip(process_args_list, process_last_frames):
                if not self.is_running:
                    break

                # 独立进程模式每帧一个新进程：上一轮的管道句柄在这里收掉，避免句柄泄漏
                if poller is not None:
                    poller.close()
                    poller = None

                self.current_process = subprocess.Popen(
                    args, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    creationflags=BLENDER_CREATE_FLAGS, bufsize=0, env=env
                )
                track_process(self.current_process)

                # 非阻塞轮询管道（详见 _PipePoller）：这里刻意不再起「读线程死等」，
                # 否则线程一旦卡在 ReadFile 里，本程序退出时就会变成终止不了的悬挂进程。
                poller = _PipePoller(self.current_process.stdout)

                if HAS_PSUTIL and getattr(self, 'cpu_pct', 1.0) <= 1.0:
                    try:
                        p = psutil.Process(self.current_process.pid)
                        total_cores = psutil.cpu_count(logical=True)
                        cores_to_use = max(1, int(total_cores * getattr(self, 'cpu_pct', 1.0)))
                        p.cpu_affinity(list(range(cores_to_use)))
                    except Exception:
                        pass

                line_buf = bytearray()
                frame_max_current = 0
                # 本进程“渲染已结束”的时刻：最后一帧渲完、或 Blender 播报退出时记录
                render_finished_at = None
                last_finalize_check = 0.0
                ended_by_watchdog = False
                # 已读出、还没逐个处理的字节（按字节处理是为了保持原有的逐行解析逻辑）
                pending = b""
                pending_pos = 0

                while self.is_running:
                    if pending_pos >= len(pending):
                        data = poller.read()
                        if data is None:
                            # 暂时没有输出：先确认进程是不是已经走了
                            if self.current_process.poll() is not None:
                                data = poller.read()
                                if data is None:
                                    data = b""
                            else:
                                # 渲染已结束但 Blender 迟迟不退出：确认帧都落盘了再主动收尾
                                if should_finalize_lingering_process(self.current_process, render_finished_at):
                                    now = time.time()
                                    if now - last_finalize_check >= 10.0:
                                        last_finalize_check = now
                                        if task_frames_present_on_disk(task):
                                            ended_by_watchdog = True
                                            self.notice.emit("log_finalize_watchdog")
                                            terminate_process_tree(self.current_process, grace=0.0)
                                            break
                                time.sleep(0.05)
                                continue
                        if data == b"":
                            # 管道关闭（Blender 已退出），把最后半行吐出去就收尾
                            if line_buf:
                                clean_line = line_buf.decode('utf-8', errors='replace').strip()
                                line_buf.clear()
                                if clean_line:
                                    self.log_updated.emit(clean_line)
                            break
                        pending = data
                        pending_pos = 0

                    byte_char = pending[pending_pos:pending_pos + 1]
                    pending_pos += 1

                    if byte_char == b'\r' or byte_char == b'\n':
                        if not line_buf:
                            continue
                        clean_line = line_buf.decode('utf-8', errors='replace').strip()
                        line_buf.clear()
                        if not clean_line:
                            continue

                        if "Blender quit" in clean_line:
                            render_finished_at = time.time()

                        lower_line = clean_line.lower()
                        if "denoising" in lower_line or "降噪" in lower_line:
                            self.sample_updated.emit(task, 1, 1, "DENOISING")

                        elif "sample" in lower_line or "采样" in lower_line:
                            tile_match = re.search(
                                r'(?:tile|rendered|区块|渲染)\D*?(\d+)\s*/\s*(\d+)\s*(?:tiles|区块)?.*?(?:sample|采样)\D*?(\d+)\s*/\s*(\d+)',
                                lower_line)

                            if tile_match:
                                num_val = int(tile_match.group(1))
                                tot_tile = int(tile_match.group(2))
                                cur_samp = int(tile_match.group(3))
                                tot_samp = int(tile_match.group(4))

                                if "rendered" in lower_line or "渲染" in lower_line:
                                    if cur_samp == tot_samp:
                                        completed_tiles = max(0, num_val - 1)
                                    else:
                                        completed_tiles = num_val
                                else:
                                    completed_tiles = max(0, num_val - 1)

                                if tot_tile > 0 and tot_samp > 0:
                                    abs_current = cur_samp + completed_tiles * tot_samp
                                    abs_total = tot_tile * tot_samp
                                    if abs_current < frame_max_current:
                                        abs_current = frame_max_current
                                    else:
                                        frame_max_current = abs_current

                                    current_tile_index = min(completed_tiles + 1, tot_tile)
                                    format_str = f"TILES:{cur_samp}:{tot_samp}:{current_tile_index}:{tot_tile}"
                                    self.sample_updated.emit(task, abs_current, abs_total, format_str)

                            else:
                                match = re.search(r'(\d+)\s*/\s*(\d+)', lower_line)
                                if match:
                                    cur_samp = int(match.group(1))
                                    tot_samp = int(match.group(2))
                                    if tot_samp > 0 and cur_samp <= tot_samp:
                                        if cur_samp < frame_max_current:
                                            cur_samp = frame_max_current
                                        else:
                                            frame_max_current = cur_samp
                                        self.sample_updated.emit(task, cur_samp, tot_samp, "")

                        self.log_updated.emit(clean_line)

                        if "Saved:" in clean_line or "Append frame" in clean_line:
                            frame_num = None
                            if "Append frame" in clean_line:
                                match = re.search(r'Append frame\s+(\d+)', clean_line)
                                if match:
                                    frame_num = match.group(1)
                            elif "Saved:" in clean_line:
                                match = re.findall(r'(\d+)\.[a-zA-Z0-9]+', clean_line)
                                if match:
                                    frame_num = match[-1]

                            # 最后一帧已渲完：从这里开始计时，用于兜底结束不退出进程
                            if reached_last_frame(frame_num, process_last_frame):
                                render_finished_at = time.time()

                            # 解析不出帧号时传空，由主线程挑一个还没统计的帧号，保证进度照常推进
                            self.frame_done.emit(task, frame_num if frame_num is not None else "")
                            frame_max_current = 0
                    else:
                        line_buf.extend(byte_char)

                if self.current_process:
                    # 必须带超时等待：Blender 若卡在驱动调用里，绝不能让本线程无限等下去
                    if not _wait_process_exit(self.current_process, 5.0):
                        terminate_process_tree(self.current_process, grace=0.0)
                    rc = self.current_process.poll()
                    # 看门狗主动结束的进程不算渲染失败
                    if rc not in (0, None) and self.is_running and not ended_by_watchdog:
                        if not getattr(task, 'error_msg', ''):
                            task.error_msg = f"Blender进程异常退出 (退出码: {rc})。\n请查看右侧日志了解详情！"
                        break

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            task.error_msg = f"Python底层启动错误:\n{str(e)}"
            self.log_updated.emit(f"❌ [进程崩溃] 启动渲染引擎失败:\n{error_trace}")

        finally:
            if temp_script and os.path.exists(temp_script):
                try:
                    os.unlink(temp_script)
                except Exception:
                    pass

            proc = self.current_process
            if proc is not None:
                if not self.is_running:
                    terminate_process_tree(proc, grace=0.0)
                elif not _wait_process_exit(proc, 3.0):
                    terminate_process_tree(proc, grace=0.0)
                else:
                    untrack_process(proc)
                    release_process_handles(proc)
                self.current_process = None

            # 管道句柄由本线程自己关（不跨线程关正在读的句柄）
            if poller is not None:
                try:
                    poller.close()
                except Exception:
                    pass
                poller = None

            if self.is_running:
                is_ok = not bool(getattr(task, 'error_msg', ''))
                self.status_updated.emit(task, "Completed" if is_ok else "Failed")

    def kill_process_tree(self, pid):
        """终止渲染子进程（优先用登记在册的 Popen 对象，其次按 PID 处理）。"""
        proc = self.current_process
        if proc is not None and getattr(proc, 'pid', None) == pid:
            terminate_process_tree(proc, grace=0.0)
        else:
            terminate_process_tree_by_pid(pid)


class QuitConfirmDialog(QDialog):
    def __init__(self, parent=None, tr_func=None):
        super().__init__(parent)
        self.tr = tr_func if tr_func else lambda key: key
        self.setWindowTitle(self.tr("warning"))
        self.setFixedSize(380, 120)
        layout = QVBoxLayout(self)
        label = QLabel(self.tr("quit_warning_text"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton(self.tr("cancel"))
        self.btn_cancel.setStyleSheet(f"background-color: {THEME_COLORS['btn_start']}; color: white; font-weight: bold; min-height: 30px;")
        self.btn_ok = QPushButton(self.tr("confirm_quit"))
        self.btn_ok.setStyleSheet(f"background-color: {THEME_COLORS['btn_stop']}; color: white; font-weight: bold; min-height: 30px;")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)


class ActionConfirmDialog(QDialog):
    def __init__(self, action_name, parent=None, tr_func=None):
        super().__init__(parent)
        self.tr = tr_func if tr_func else lambda key: key
        self.action_name = action_name
        self.countdown = 10
        self.setWindowTitle(self.tr("render_complete_prompt"))
        self.setFixedSize(400, 150)
        layout = QVBoxLayout(self)
        self.tip_label = QLabel(self.tr("tasks_completed_tip").format(action=self.action_name, countdown=self.countdown))
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tip_label)
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton(self.tr("cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        self.immediate_btn = QPushButton(self.tr("execute_now").format(action=self.action_name))
        self.immediate_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.immediate_btn)
        layout.addLayout(btn_layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.timer.stop()
            self.accept()
        self.tip_label.setText(self.tr("tasks_completed_tip").format(action=self.action_name, countdown=self.countdown))


_NVML_LOCK = threading.Lock()
_NVML_STATE = {"tried": False, "module": None}


def _nvml_module():
    """取得已 nvmlInit() 过的 pynvml 模块（只初始化一次，永不 Shutdown）。

    这是全局单例，多个轮询线程共用同一个已初始化的 NVML 会话；
    重复 Init/Shutdown 会反复加载/卸载 nvml.dll，是驱动不稳定的常见诱因。
    """
    with _NVML_LOCK:
        if not _NVML_STATE["tried"]:
            _NVML_STATE["tried"] = True
            try:
                import pynvml
                pynvml.nvmlInit()
                _NVML_STATE["module"] = pynvml
            except Exception:
                _NVML_STATE["module"] = None
        return _NVML_STATE["module"]


class MainWindow(QMainWindow):

    def save_session(self, blocking=False):
        try:
            current_row = self.task_list.currentRow()
            log_content = self.log_out.toHtml()
            data_to_save = {
                "current_row": current_row,
                "tasks": [t.to_dict() for t in self.tasks],
                "log_content": log_content
            }
        except Exception:
            return

        if blocking:
            # 退出流程里必须同步写完，否则进程一结束就可能丢数据
            self._write_to_disk_task(data_to_save)
            return

        try:
            write_thread = threading.Thread(
                target=self._write_to_disk_task,
                args=(data_to_save,),
                daemon=True
            )
            write_thread.start()
        except Exception:
            pass

    def _write_to_disk_task(self, data):
        # 先写临时文件再替换，避免写入中途被打断导致会话文件损坏
        tmp_file = SESSION_FILE + ".tmp"
        with _SESSION_LOCK:
            try:
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                os.replace(tmp_file, SESSION_FILE)
            except Exception:
                try:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                except Exception:
                    pass

    def load_session(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.tasks = [RenderTask.from_dict(td) for td in data.get("tasks", [])]
                if "log_content" in data:
                    self.log_out.setHtml(data["log_content"])

                for t in self.tasks:
                    if t.status == "Rendering":
                        t.status = "Stopped"

                self.refresh_ui()

                current_row = data.get("current_row", -1)
                if 0 <= current_row < len(self.tasks):
                    self.task_list.setCurrentRow(current_row)
                elif len(self.tasks) > 0:
                    self.task_list.setCurrentRow(0)
            except Exception:
                pass

    def on_scene_switched(self, new_scene):
        if not self.current_task or not new_scene or not self.middle_panel.isEnabled():
            return
        t = self.current_task
        t.scene_name = new_scene
        if hasattr(t, 'scene_data') and new_scene in t.scene_data:
            sd = t.scene_data[new_scene]
            self.block_signals(True)
            self.camera_cb.clear()
            self.camera_cb.addItems(sd.get('cl', []))
            self.camera_cb.setCurrentText(sd.get('cc', ""))
            self.f_start.setText(str(sd.get('fs', 1)))
            self.f_end.setText(str(sd.get('fe', 250)))
            self.f_step.setText(str(sd.get('st', 1)))
            self.res_x.setText(str(sd.get('rx', 1920)))
            self.res_y.setText(str(sd.get('ry', 1080)))
            self.out_path_edit.setText(sd.get('out', ""))
            self.fmt_cb.setCurrentText(sd.get('fm', "PNG"))
            self.block_signals(False)
            self.save_ui_to_task()

    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.current_lang = "zh"
        self.extractors = []
        self.tasks = []
        self.blender_path = ""
        self.current_task = None
        self.workers = []
        self.is_rendering = False
        self._exiting = False
        # 计时统一放在每个 RenderTask 上（并行渲染时各任务互不干扰）
        self.batch_start_time = time.time()
        self._last_disk_rescan = 0.0
        # 显卡信息在后台线程里取（见 poll_gpu_async）：绝不在 GUI 线程里调显卡驱动。
        #
        # 默认关闭，这是有实证依据的决定（2026-10-24 的诊断快照）：
        # 卡死进程里 threads=1、该线程状态不是 Wait（= 正在内核态里跑，不在等事件）、
        # handles=1120、窗口已销毁但进程不退 —— 这就是 Windows「终止中」状态的签名：
        # 内核已经杀掉它所有能杀的线程，只剩一个卡在不可取消的内核调用里的线程。
        # 同一进程的已加载模块里有 nvml.dll（pynvml 用的就是它），所以那个线程极可能
        # 就是卡在显卡驱动里的 NVML 调用上。这种线程用户态永远杀不掉，进程只能重启。
        #
        # 显卡数字只是「好看」，不值得拿整个程序的可退出性去换。
        # 需要的话在配置里写 "gpu_monitor": true 显式打开。
        self._gpu_lock = threading.Lock()
        self._gpu_info = ("--", "--")
        self._gpu_polling = False
        self._gpu_poll_started_at = 0.0
        self._gpu_poll_slow = False      # 出现过一次「很久没返回」就永久停用显卡监控
        self.gpu_monitor = False
        self._shutdown_thread = None
        self._shutdown_done = threading.Event()
        self._exit_timer = None

        try:
            icon = QIcon(resource_path("favicon.ico"))
            self.setWindowIcon(icon)
        except Exception:
            pass

        self.spinner_frames = ["|", "/", "-", "\\"]
        self.spinner_idx = 0
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.spinner_timer.start(150)
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_system_resources)
        self.monitor_timer.start(1000)

        self.setAcceptDrops(True)
        self.init_ui()
        self.load_config()
        log_exit("启动：显卡监控=%r（关闭时不会向显卡驱动发任何查询）" % (
            getattr(self, 'gpu_monitor', False),))
        self.apply_theme()
        self.retranslate_ui()
        self.load_session()

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def switch_language(self):
        self.block_signals(True)
        try:
            self.current_lang = "en" if self.current_lang == "zh" else "zh"
            self.retranslate_ui()
            self.save_config()
            self.on_selection_changed()
        finally:
            self.block_signals(False)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("title"))
        self.top_box.setTitle(self.tr("blender_group"))
        self.btn_set_b.setText(self.tr("set_path"))
        self.lang_btn.setText(self.tr("lang_btn"))
        self.left_box.setTitle(self.tr("project_list"))
        btn_texts = [
            ("import", self.import_btn), ("copy", self.copy_btn), ("delete", self.delete_btn),
            ("refresh", self.refresh_btn), ("reset", self.reset_btn), ("clear", self.clear_btn),
            ("open_blend", self.open_blend_btn),
        ]
        for tr_key, btn in btn_texts:
            btn.setText(self.tr(tr_key))
        self.middle_panel.setTitle(self.tr("params_group"))
        self.label_scene.setText(self.tr("scene"))
        self.label_camera.setText(self.tr("camera"))
        self.label_rx.setText(self.tr("res_x"))
        self.label_ry.setText(self.tr("res_y"))
        self.label_format.setText(self.tr("format"))
        self.label_start.setText(self.tr("start_frame"))
        self.label_end.setText(self.tr("end_frame"))
        self.label_step.setText(self.tr("step_frame"))
        self.label_cf.setText(self.tr("custom_frames"))
        if hasattr(self, 'btn_clear_cf'):
            self.btn_clear_cf.setText(self.tr("clear_cf"))
        if hasattr(self, 'btn_auto_fill'):
            self.btn_auto_fill.setText(self.tr("auto_fill"))
        self.label_output.setText(self.tr("output_path"))
        self.label_after.setText(self.tr("after"))
        self.custom_frames_edit.setPlaceholderText(self.tr("custom_frames_ph"))
        self.btn_browse.setText(self.tr("browse"))
        if hasattr(self, 'indep_process_cb'):
            self.indep_process_cb.setText(self.tr("indep_process"))
            self.indep_process_cb.setToolTip(self.tr("indep_process_tt"))
        self.block_signals(True)
        current_action = self.after_render_action.currentData()
        self.after_render_action.clear()
        action_config = [
            ("none", "None"), ("shutdown", "Shut Down"),
            ("sleep", "Sleep"), ("restart", "Restart")
        ]
        for tr_key, data_val in action_config:
            self.after_render_action.addItem(self.tr(tr_key), data_val)
        if current_action:
            index = self.after_render_action.findData(current_action)
            if index >= 0:
                self.after_render_action.setCurrentIndex(index)
        self.block_signals(False)
        self.control_panel.setTitle(self.tr("control_group"))
        self.btn_start.setText(self.tr("start"))
        self.btn_stop.setText(self.tr("stop"))

        if hasattr(self, 'cpu_limit_cb'):
            current_cpu = self.cpu_limit_cb.currentData() or 1.0
            self.cpu_limit_label.setText(self.tr("cpu_limit"))
            self.cpu_limit_cb.blockSignals(True)
            self.cpu_limit_cb.clear()
            self.cpu_limit_cb.addItem(self.tr("cpu_100"), 1.0)
            self.cpu_limit_cb.addItem(self.tr("cpu_75"), 0.75)
            self.cpu_limit_cb.addItem(self.tr("cpu_50"), 0.5)
            self.cpu_limit_cb.addItem(self.tr("cpu_25"), 0.25)
            idx = self.cpu_limit_cb.findData(current_cpu)
            if idx >= 0:
                self.cpu_limit_cb.setCurrentIndex(idx)
            self.cpu_limit_cb.blockSignals(False)

        if hasattr(self, 'parallel_label'):
            self.parallel_label.setText(self.tr("parallel_label"))

        self.res_label.setText(self.tr("system_usage"))
        self.update_stat()
        self.btn_clear_log.setText(self.tr("clear_log"))

        if hasattr(self, 'frame_progress_bar'):
            self.frame_progress_bar.setMaximum(1)
            self.frame_progress_bar.setValue(0)
            self.frame_progress_bar.setFormat(self.tr("frame_sample").replace('%v', '--').replace('%m', '--'))

        if hasattr(self, 'progress_bar'):
            self.progress_bar.setFormat(self.tr("total_progress"))

        self.refresh_ui()

    def update_spinner(self):
        self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
        self.refresh_ui()
        self.refresh_progress_from_disk()

    def refresh_progress_from_disk(self, interval=15.0):
        """渲染过程中定期把输出目录里已经渲好的帧并入进度（只增不减）。

        兜底用：万一开始渲染时没能识别出已有帧（路径/命名有差异），
        或者这些帧是在本程序之外产生的，进度也不会一直停在 0%。
        """
        if not self.is_rendering:
            return
        now = time.time()
        if now - getattr(self, '_last_disk_rescan', 0.0) < interval:
            return
        self._last_disk_rescan = now
        changed = False
        for t in self.tasks:
            if getattr(t, 'status', '') != "Rendering":
                continue
            found = scan_existing_frames(t)
            if not found:
                continue
            missing = found - t.rendered_frame_set
            if missing:
                t.rendered_frame_set |= missing
                t.rendered_frames = len(t.rendered_frame_set)
                changed = True
        if changed:
            self.update_stat()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {THEME_COLORS['bg_app']};
                color: {THEME_COLORS['text_main']};
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: 13px;
            }}
            QLabel {{ background-color: transparent; }}
            QSplitter::handle {{ background-color: transparent; }}
            QSplitter::handle:hover {{ background-color: {THEME_COLORS['accent']}; }}
            QGroupBox {{
                background-color: {THEME_COLORS['bg_panel']};
                border: 1px solid {THEME_COLORS['bg_panel']};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                top: 4px;
                color: {THEME_COLORS['text_muted']};
                font-weight: bold;
                font-size: 12px;
                background-color: transparent;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {THEME_COLORS['bg_input']};
                color: {THEME_COLORS['text_main']};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 24px;
            }}
            QLineEdit:hover, QComboBox:hover {{ background-color: {THEME_COLORS['bg_input_hover']}; }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{ border: 1px solid {THEME_COLORS['border_focus']}; }}
            QLineEdit:disabled, QComboBox:disabled {{ color: {THEME_COLORS['text_muted']}; background-color: {THEME_COLORS['bg_app']}; }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
            QComboBox QAbstractItemView {{
                background-color: {THEME_COLORS['bg_panel']};
                border: 1px solid {THEME_COLORS['border_light']};
                border-radius: 6px;
                outline: none;
            }}
            QListWidget {{
                background-color: {THEME_COLORS['bg_app']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: {THEME_COLORS['bg_panel']};
                border: 1px solid rgba(255, 255, 255, 0.33);
                border-radius: 2px;
                margin-top: 4px;
                margin-left: 4px;
                margin-right: 4px;
                padding: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {THEME_COLORS['border_light']};
                border-left: 4px solid {THEME_COLORS['accent']};
                color: {THEME_COLORS['text_main']};
            }}
            QPushButton {{
                background-color: {THEME_COLORS['bg_input']};
                color: {THEME_COLORS['text_main']};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 26px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {THEME_COLORS['bg_input_hover']}; }}
            QPushButton:pressed {{ background-color: {THEME_COLORS['border_light']}; }}
            QPushButton#btn_start {{ background-color: {THEME_COLORS['btn_start']}; font-weight: bold; color: white; min-height: 24px; }}
            QPushButton#btn_start:hover {{ background-color: {THEME_COLORS['btn_start_hover']}; }}
            QPushButton#btn_stop {{ background-color: {THEME_COLORS['btn_stop']}; font-weight: bold; color: white; min-height: 24px; }}
            QPushButton#btn_stop:hover {{ background-color: {THEME_COLORS['btn_stop_hover']}; }}
            QProgressBar {{
                border: none;
                border-radius: 6px;
                text-align: center;
                background-color: {THEME_COLORS['progress_bg']};
                color: {THEME_COLORS['text_main']};
                font-weight: bold;
                min-height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {THEME_COLORS['progress_chunk']};
                border-radius: 6px;
            }}
            QScrollBar:vertical {{ border: none; background: transparent; width: 10px; margin: 0px 0px 0px 0px; }}
            QScrollBar::handle:vertical {{ background: {THEME_COLORS['text_muted']}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::handle:vertical:hover {{ background: {THEME_COLORS['text_main']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            QCheckBox {{
                background-color: transparent;
                color: {THEME_COLORS['text_muted']};
                spacing: 8px;
            }}
            QCheckBox:hover {{ color: {THEME_COLORS['text_main']}; }}
            QCheckBox:disabled {{ color: {THEME_COLORS['bg_input_hover']}; }}
        """)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.top_box = QGroupBox()
        self.top_box.setMinimumHeight(95)
        self.top_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        top_lay = QHBoxLayout(self.top_box)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.btn_set_b = QPushButton()
        self.btn_set_b.clicked.connect(self.select_blender_path)
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(100)
        self.lang_btn.clicked.connect(self.switch_language)
        top_lay.addWidget(self.path_edit)
        top_lay.addWidget(self.btn_set_b)
        top_lay.addWidget(self.lang_btn)
        main_layout.addWidget(self.top_box)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        self.left_box = QGroupBox()
        self.left_box.setMinimumWidth(300)
        left_lay = QVBoxLayout(self.left_box)
        self.task_list = QListWidget()
        self.task_list.setItemDelegate(MyDelegate())
        self.task_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.task_list.setDragEnabled(True)
        self.task_list.setAcceptDrops(True)
        self.task_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.task_list.installEventFilter(self)
        self.task_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.task_list.itemDoubleClicked.connect(self.check_error_detail)
        left_lay.addWidget(self.task_list)

        list_grid = QGridLayout()
        btns_config = [
            ("import", self.add_task_dialog), ("copy", self.copy_task), ("delete", self.remove_task),
            ("refresh", self.refresh_task_params), ("reset", self.reset_tasks), ("clear", self.clear_tasks),
            ("open_blend", self.open_in_blender),
        ]
        self.import_btn = self.copy_btn = self.delete_btn = None
        self.refresh_btn = self.reset_btn = self.clear_btn = None
        self.open_blend_btn = None
        for i, (tr_key, func) in enumerate(btns_config):
            b = QPushButton()
            b.clicked.connect(func)
            row = i // 3
            col = i % 3
            span = 3 if tr_key == "open_blend" else 1
            list_grid.addWidget(b, row, col, 1, span)
            setattr(self, f"{tr_key}_btn", b)
        left_lay.addLayout(list_grid)
        self.stat_label = QLabel()
        left_lay.addWidget(self.stat_label)
        self.main_splitter.addWidget(self.left_box)

        right_v_splitter = QSplitter(Qt.Orientation.Vertical)
        right_v_splitter.setChildrenCollapsible(False)

        self.middle_panel = QGroupBox()
        self.middle_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        param_layout = QVBoxLayout(self.middle_panel)

        self.scene_cb = QComboBox()
        self.scene_cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.camera_cb = QComboBox()
        self.camera_cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.fmt_cb = QComboBox()
        self.fmt_cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.fmt_cb.addItems(["PNG", "JPEG", "TIFF", "OPEN_EXR", "AVI_JPEG", "FFMPEG"])

        self.out_path_edit = QLineEdit()
        self.btn_browse = QPushButton()
        self.btn_browse.setFixedWidth(80)
        self.btn_browse.clicked.connect(self.select_output_path)
        self.f_start = QLineEdit()
        self.f_end = QLineEdit()
        self.f_step = QLineEdit()
        self.res_x = QLineEdit()
        self.res_y = QLineEdit()

        self.after_render_action = QComboBox()
        self.after_render_action.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        form = QGridLayout()

        self.label_scene = QLabel()
        self.label_camera = QLabel()

        form.addWidget(self.label_scene, 0, 0)

        row0_lay = QHBoxLayout()
        row0_lay.setContentsMargins(0, 0, 0, 0)
        row0_lay.addWidget(self.scene_cb, 1)
        row0_lay.addSpacing(15)
        row0_lay.addWidget(self.label_camera)
        row0_lay.addWidget(self.camera_cb, 1)

        form.addLayout(row0_lay, 0, 1, 1, 5)

        self.label_rx = QLabel()
        self.label_ry = QLabel()
        self.label_format = QLabel()
        form.addWidget(self.label_rx, 1, 0)
        form.addWidget(self.res_x, 1, 1)
        form.addWidget(self.label_ry, 1, 2)
        form.addWidget(self.res_y, 1, 3)
        form.addWidget(self.label_format, 1, 4)
        form.addWidget(self.fmt_cb, 1, 5)

        self.label_start = QLabel()
        self.label_end = QLabel()
        self.label_step = QLabel()
        form.addWidget(self.label_start, 2, 0)
        form.addWidget(self.f_start, 2, 1)
        form.addWidget(self.label_end, 2, 2)
        form.addWidget(self.f_end, 2, 3)
        form.addWidget(self.label_step, 2, 4)
        form.addWidget(self.f_step, 2, 5)

        self.label_cf = QLabel()
        self.custom_frames_edit = QLineEdit()
        self.custom_frames_edit.textChanged.connect(self.on_custom_frames_changed)
        self.custom_frames_edit.editingFinished.connect(self.validate_and_save_custom_frames)

        self.btn_clear_cf = QPushButton()
        self.btn_clear_cf.clicked.connect(self.clear_custom_frames)
        self.btn_auto_fill = QPushButton()
        self.btn_auto_fill.clicked.connect(self.auto_fill_missing_frames)

        form.addWidget(self.label_cf, 3, 0)
        form.addWidget(self.custom_frames_edit, 3, 1, 1, 3)
        form.addWidget(self.btn_clear_cf, 3, 4)
        form.addWidget(self.btn_auto_fill, 3, 5)

        self.label_output = QLabel()
        form.addWidget(self.label_output, 4, 0)
        output_lay = QHBoxLayout()
        output_lay.setContentsMargins(0, 0, 0, 0)
        output_lay.addWidget(self.out_path_edit)
        output_lay.addWidget(self.btn_browse)
        form.addLayout(output_lay, 4, 1, 1, 5)

        self.label_after = QLabel()
        form.addWidget(self.label_after, 5, 0)
        form.addWidget(self.after_render_action, 5, 1, 1, 2)

        self.indep_process_cb = QCheckBox()
        self.indep_process_cb.clicked.connect(self.save_ui_to_task)
        form.addWidget(self.indep_process_cb, 5, 3, 1, 3, Qt.AlignmentFlag.AlignRight)
        param_layout.addLayout(form)

        self.control_panel = QGroupBox()
        self.control_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        control_lay = QVBoxLayout(self.control_panel)
        self.res_label = QLabel()
        self.btn_start = QPushButton()
        self.btn_start.setObjectName("btn_start")
        self.time_label = QLabel()
        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.hide()

        self.cpu_limit_label = QLabel()
        self.cpu_limit_cb = QComboBox()
        self.cpu_limit_cb.currentIndexChanged.connect(self.apply_cpu_affinity)

        self.parallel_label = QLabel()
        self.parallel_cb = QComboBox()
        for n in range(1, 9):
            self.parallel_cb.addItem(str(n), n)
        self.parallel_cb.setCurrentIndex(0)

        cpu_lay = QHBoxLayout()
        cpu_lay.addWidget(self.cpu_limit_label)
        cpu_lay.addWidget(self.cpu_limit_cb)
        cpu_lay.addSpacing(15)
        cpu_lay.addWidget(self.parallel_label)
        cpu_lay.addWidget(self.parallel_cb)
        cpu_lay.addStretch()
        control_lay.addLayout(cpu_lay)

        self.btn_start.clicked.connect(self.start_render)
        self.btn_stop.clicked.connect(self.stop_render)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat(self.tr("total_progress"))
        self.frame_progress_bar = QProgressBar()
        self.frame_progress_bar.setFormat(self.tr("frame_sample").replace('%v', '--').replace('%m', '--'))

        control_lay.addWidget(self.res_label)
        control_lay.addWidget(self.time_label)
        control_lay.addWidget(self.btn_start)
        control_lay.addWidget(self.btn_stop)

        progress_lay = QHBoxLayout()
        progress_lay.addWidget(self.progress_bar)
        progress_lay.addWidget(self.frame_progress_bar)
        control_lay.addLayout(progress_lay)

        right_v_splitter.addWidget(self.middle_panel)
        right_v_splitter.addWidget(self.control_panel)

        log_container = QWidget()
        log_lay = QVBoxLayout(log_container)
        log_lay.setContentsMargins(0, 0, 0, 0)
        self.log_out = QTextEdit()
        self.log_out.setReadOnly(True)
        self.btn_clear_log = QPushButton()
        self.btn_clear_log.clicked.connect(self.log_out.clear)
        log_lay.addWidget(self.log_out)
        log_lay.addWidget(self.btn_clear_log)

        right_v_splitter.addWidget(log_container)
        right_v_splitter.setStretchFactor(0, 0)
        right_v_splitter.setStretchFactor(1, 0)
        right_v_splitter.setStretchFactor(2, 1)

        self.main_splitter.addWidget(right_v_splitter)
        self.main_splitter.setSizes([500, 600])
        main_layout.addWidget(self.main_splitter)

        self.scene_cb.currentTextChanged.connect(self.on_scene_switched)
        for w in [self.camera_cb, self.fmt_cb, self.after_render_action]:
            w.currentTextChanged.connect(self.save_ui_to_task)
        for w in [self.f_start, self.f_end, self.f_step, self.res_x, self.res_y, self.out_path_edit]:
            w.editingFinished.connect(self.save_ui_to_task)

    def eventFilter(self, source, event):
        if source is self.task_list:
            if event.type() == event.Type.MouseButtonPress:
                if not self.task_list.itemAt(event.pos()):
                    self.task_list.clearSelection()
            elif event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_Delete:
                    self.remove_task()
                    return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        event.ignore()
        if getattr(self, '_exiting', False):
            return
        if self.is_rendering:
            dialog = QuitConfirmDialog(self, self.tr)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
        self.cleanup_and_quit()

    def cleanup_and_quit(self):
        """退出：GUI 线程只做「极快、绝不阻塞」的事，其余全部交给后台线程。

        这就是之前「关闭时拒绝访问 + 系统卡顿 + 只能重启」的直接对策：
          * GUI 线程绝不去等子进程、等线程、等显卡驱动 —— 一旦它卡住，窗口就
            变成「未响应」，用户只能在任务管理器里强杀，而强杀一个正在收尾的
            进程恰好就是「拒绝访问」的来源；
          * 清理工作全部后台化，并且有总时限；
          * 无论如何都有一个硬上限，到点直接结束本进程。
        """
        if getattr(self, '_exiting', False):
            return
        self._exiting = True
        started = time.time()

        # ---- 1. 停掉 Qt 定时器（必须在 GUI 线程）----
        for timer_name in ('monitor_timer', 'spinner_timer'):
            timer = getattr(self, timer_name, None)
            if timer is not None:
                try:
                    timer.stop()
                except Exception:
                    pass

        # ---- 2. 复位电源状态（必须在 GUI 线程、必须做）----
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            pass

        # ---- 3. 通知 worker 别再取任务，并把渲染中的任务记成“手动停止” ----
        workers = list(getattr(self, 'workers', []) or [])
        for w in workers:
            try:
                w.is_running = False
            except Exception:
                pass
            task = getattr(w, 'current_rendering_task', None)
            if task is not None:
                task.status = "Stopped"
        self.is_rendering = False

        # ---- 4. 需要落盘的内容在 GUI 线程取好（后台线程不允许碰控件）----
        payload = None
        try:
            payload = {
                "current_row": self.task_list.currentRow(),
                "tasks": [t.to_dict() for t in self.tasks],
                "log_content": self.log_out.toHtml(),
            }
        except Exception:
            payload = None
        config_data = None
        try:
            config_data = self._config_payload()
        except Exception:
            config_data = None

        # ---- 5. 关掉单实例服务（Qt 对象，仍留在 GUI 线程）----
        try:
            if _LOCAL_SERVER is not None:
                _LOCAL_SERVER.close()
            QLocalServer.removeServer(SERVER_NAME)
        except Exception:
            pass

        # ---- 6. 窗口立刻进入“正在退出”的可读状态，不会让人以为卡死了 ----
        try:
            self.setWindowTitle(self.tr("exiting_tip"))
            self.centralWidget().setEnabled(False)
        except Exception:
            pass

        # ---- 7. 剩下的活全部甩到后台线程，GUI 线程立刻返回事件循环 ----
        extractors = list(getattr(self, 'extractors', []) or [])
        self._shutdown_done.clear()
        # 后台清理完成后，由 GUI 主线程来做最后一步「结束本进程」：
        # ExitProcess/TerminateProcess 从非主线程调用会去抢加载器锁，而主线程此刻
        # 正待在 Qt 事件循环里 —— 那是一个真实的死锁点。所以这里用一个定时器
        # 在主线程上收尾，后台线程只负责把 _shutdown_done 置位。
        self._exit_timer = QTimer(self)
        self._exit_timer.timeout.connect(self._final_exit_if_ready)
        self._exit_timer.start(60)
        # 先挂好看门狗：哪怕下面启动清理线程失败，也一定会退出
        threading.Thread(target=self._exit_watchdog, daemon=True).start()
        self._shutdown_thread = threading.Thread(
            target=self._shutdown_worker,
            args=(workers, extractors, payload, config_data, started),
            daemon=True,
        )
        try:
            self._shutdown_thread.start()
        except Exception as exc:
            log_exit("启动退出清理线程失败：%r，直接结束本进程。" % (exc,))
            force_exit(1, why="start-shutdown-thread-failed")

    def _final_exit_if_ready(self):
        """（GUI 主线程）后台清理完成后的最后一步：结束本进程。"""
        if not self._shutdown_done.is_set():
            return
        try:
            self._exit_timer.stop()
        except Exception:
            pass
        log_exit("后台清理已完成，由 GUI 主线程结束本进程。")
        force_exit(0, why="main-thread")

    def _exit_watchdog(self):
        """硬上限：即使后台清理 / 主线程收尾被卡住，也绝不无限期挂在退出流程里。"""
        time.sleep(SHUTDOWN_HARD_LIMIT)
        try:
            names = sorted({t.name for t in threading.enumerate()})
            log_exit("看门狗触发（%.0fs）：后台清理%s完成；存活线程(%d)：%s" % (
                SHUTDOWN_HARD_LIMIT,
                "已" if self._shutdown_done.is_set() else "未",
                len(names), ", ".join(names)))
        except Exception:
            log_exit("看门狗触发（%.0fs），强制结束本进程。" % SHUTDOWN_HARD_LIMIT)
        force_exit(1, why="watchdog")

    def _shutdown_worker(self, workers, extractors, payload, config_data, started):
        """后台线程：限时结束子进程 -> 落盘 -> 结束本进程。

        这里做的每一件事都带时限，任何一步失败都只记日志，绝不阻塞退出。
        """
        denied = []
        try:
            log_exit("开始退出：workers=%d extractors=%d 显卡监控=%r" % (
                len(workers), len(extractors), getattr(self, 'gpu_monitor', False)))

            # 1) worker 自己启动的 Blender：批量、共用一个截止时间
            procs = [getattr(w, 'current_process', None) for w in workers]
            denied += stop_processes(procs, grace=0.3, force_timeout=SHUTDOWN_KILL_BUDGET)

            # 2) 参数提取线程（它们也可能挂着 Blender）。等待预算共用一个，不逐个累加
            for ext in extractors:
                try:
                    ext.stop()
                except Exception:
                    pass
            ext_deadline = time.time() + 1.2
            for ext in extractors:
                left = ext_deadline - time.time()
                if left <= 0:
                    break
                try:
                    ext.wait(int(left * 1000))
                except Exception:
                    pass

            # 3) 兜底再清一遍：登记在册的 + 名下的 Blender 子进程
            #    （独立进程模式下 worker 可能刚好又拉起了一个新进程）
            denied += terminate_all_tracked_processes(grace=0.0, force_timeout=1.2)
            denied += sweep_orphan_children(force_timeout=1.2)
            # 最后再点名一次：明明已经 kill 过、却还活着（Popen.poll() 仍为 None），
            # 那就是 Windows 意义上的「终止中 / 拒绝访问」，必须如实记下来
            denied += _alive_pids(procs)
            denied = sorted({int(pid) for pid in denied if pid})

            if denied:
                log_exit("以下进程结束不了（系统返回拒绝访问），已放弃并继续退出：%s" % denied)
                if payload is not None:
                    payload["log_content"] = (payload.get("log_content") or "") + (
                        "<p>⚠️ 退出时仍有进程无法结束（系统返回“拒绝访问”）：%s。<br>"
                        "这通常说明该进程已经卡在显卡驱动里、进入了系统级“终止中”状态，"
                        "任务管理器 / taskkill /F 同样结束不了它，只能重启电脑彻底清掉。"
                        "</p>" % denied)
        except Exception as exc:
            log_exit("退出清理出错：%r" % (exc,))

        # 4) 落盘（必须在结束进程之前完成，否则会丢任务列表和日志）
        try:
            if payload is not None:
                self._write_to_disk_task(payload)
        except Exception as exc:
            log_exit("保存会话失败：%r" % (exc,))
        try:
            if config_data is not None:
                write_config_to_disk(config_data)
        except Exception as exc:
            log_exit("保存配置失败：%r" % (exc,))

        # 5) 退出诊断：把「谁还活着」记下来。这几行是定位「关不掉」的关键证据。
        try:
            with self._gpu_lock:
                gpu_info = tuple(self._gpu_info)
            if self._gpu_polling:
                log_exit("注意：退出时仍有一次显卡驱动查询(NVML/ADL)没有返回（已挂起 %.1fs），"
                         "它很可能永久卡在驱动里，并会阻止本进程被彻底终止。"
                         % (time.time() - getattr(self, '_gpu_poll_started_at', 0.0)))
            log_exit("显卡信息=%r 显卡监控=%r" % (gpu_info, getattr(self, 'gpu_monitor', True)))
            names = sorted({t.name for t in threading.enumerate()})
            log_exit("退出时存活的线程(%d)：%s" % (len(names), ", ".join(names)))
        except Exception as exc:
            log_exit("退出诊断信息收集失败：%r" % (exc,))

        # 6) 清理完成，把收尾交给 GUI 主线程（见 _final_exit_if_ready）
        log_exit("清理完成，用时 %.2fs，等待主线程结束进程。" % (time.time() - started))
        self._shutdown_done.set()

    def refresh_ui(self):
        if self.task_list.count() != len(self.tasks):
            self.task_list.clear()
            for t in self.tasks:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, t)
                self.task_list.addItem(item)
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            t = item.data(Qt.ItemDataRole.UserRole)

            if t.load_status == "Loading":
                status_text = self.tr("status_loading")
                item.setText(f"{self.spinner_frames[self.spinner_idx]} [{status_text}] {t.name}")
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
                item.setForeground(QBrush(QColor(THEME_COLORS['list_wait'])))
            elif t.load_status == "Failed" or t.status == "Failed":
                item.setText(f"[{self.tr('status_failed')}] {t.name} (双击查看详情)")
                item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
                item.setForeground(QBrush(QColor(THEME_COLORS['list_failed'])))
            else:
                status_map = {
                    "Waiting": "status_waiting",
                    "Rendering": "status_rendering",
                    "Completed": "status_completed",
                    "Stopped": "status_stopped",
                    "Failed": "status_failed"
                }
                status_key = status_map.get(t.status, "status_waiting")
                status_text = self.tr(status_key)

                if t.status == "Rendering":
                    item.setText(f"{self.spinner_frames[self.spinner_idx]} [{status_text}] {t.name}")
                    item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
                    item.setForeground(QBrush(QColor(THEME_COLORS['list_running'])))
                elif t.status == "Waiting":
                    item.setText(f"[{status_text}] {t.name}")
                    item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
                    item.setForeground(QBrush(QColor(THEME_COLORS['list_wait'])))
                elif t.status == "Completed":
                    item.setText(f"[{status_text}] {t.name}")
                    item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
                    item.setForeground(QBrush(QColor(THEME_COLORS['list_complete'])))
                elif t.status == "Stopped":
                    item.setText(f"[{status_text}] {t.name}")
                    item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
                    item.setForeground(QBrush(QColor(THEME_COLORS['list_stopped'])))

        self.tasks = [self.task_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.task_list.count())]
        self.update_stat()

    def on_selection_changed(self):
        sel = self.task_list.selectedItems()
        self.block_signals(True)

        if not sel:
            self.middle_panel.setEnabled(True)
            self.scene_cb.clear()
            self.camera_cb.clear()
            self.f_start.setText("")
            self.f_end.setText("")
            self.f_step.setText("")
            self.res_x.setText("")
            self.res_y.setText("")
            self.out_path_edit.setText("")
            self.custom_frames_edit.setText("")
            self.fmt_cb.setCurrentIndex(0)

            self.scene_cb.setEnabled(False)
            self.camera_cb.setEnabled(False)
            self.f_start.setEnabled(False)
            self.f_end.setEnabled(False)
            self.f_step.setEnabled(False)
            self.res_x.setEnabled(False)
            self.res_y.setEnabled(False)
            self.out_path_edit.setEnabled(False)
            self.custom_frames_edit.setEnabled(False)
            self.fmt_cb.setEnabled(False)
            self.btn_browse.setEnabled(False)

            if hasattr(self, 'btn_clear_cf'):
                self.btn_clear_cf.setEnabled(False)
            if hasattr(self, 'btn_auto_fill'):
                self.btn_auto_fill.setEnabled(False)
            if hasattr(self, 'indep_process_cb'):
                self.indep_process_cb.setEnabled(False)
                self.indep_process_cb.setChecked(False)

            self.after_render_action.setEnabled(True)
            self.block_signals(False)
            return

        t = sel[-1].data(Qt.ItemDataRole.UserRole)
        self.current_task = t
        is_locked = t.status in ["Rendering", "Completed"]
        load_success = t.load_status == "Success"

        self.middle_panel.setEnabled(load_success)
        self.scene_cb.setEnabled(load_success and not is_locked)
        self.camera_cb.setEnabled(load_success and not is_locked)
        self.res_x.setEnabled(load_success and not is_locked)
        self.res_y.setEnabled(load_success and not is_locked)
        self.out_path_edit.setEnabled(load_success and not is_locked)
        self.fmt_cb.setEnabled(load_success and not is_locked)
        self.btn_browse.setEnabled(load_success and not is_locked)

        if hasattr(self, 'btn_clear_cf'):
            self.btn_clear_cf.setEnabled(load_success and not is_locked)
        if hasattr(self, 'btn_auto_fill'):
            self.btn_auto_fill.setEnabled(load_success and not is_locked)

        self.after_render_action.setEnabled(load_success)

        self.scene_cb.clear()
        self.scene_cb.addItems(t.scenes_list)
        self.scene_cb.setCurrentText(t.scene_name)
        self.camera_cb.clear()
        self.camera_cb.addItems(t.cameras_list)
        self.camera_cb.setCurrentText(t.camera_name)
        self.res_x.setText(str(t.resolution_x))
        self.res_y.setText(str(t.resolution_y))
        self.out_path_edit.setText(t.output_path)
        self.fmt_cb.setCurrentText(t.output_format)

        cf = getattr(t, 'custom_frames', '')
        self.custom_frames_edit.setText(cf)
        self.custom_frames_edit.setEnabled(load_success and not is_locked)

        if cf.strip():
            self.f_start.setText("")
            self.f_end.setText("")
            self.f_step.setText("")
            self.f_start.setEnabled(False)
            self.f_end.setEnabled(False)
            self.f_step.setEnabled(False)
        else:
            self.f_start.setText(str(t.frame_start))
            self.f_end.setText(str(t.frame_end))
            self.f_step.setText(str(t.frame_step))
            self.f_start.setEnabled(load_success and not is_locked)
            self.f_end.setEnabled(load_success and not is_locked)
            self.f_step.setEnabled(load_success and not is_locked)

        if hasattr(self, 'indep_process_cb'):
            self.indep_process_cb.setEnabled(load_success and not is_locked)
            self.indep_process_cb.setChecked(getattr(t, 'independent_process', False))

        self.block_signals(False)

    def reset_tasks(self):
        items = self.task_list.selectedItems()
        if not items:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_task_warn"))
            return
        for i in items:
            t = i.data(Qt.ItemDataRole.UserRole)
            t.status = "Waiting"
            t.set_rendered_frames(())
        self.refresh_ui()
        self.on_selection_changed()

    def refresh_task_params(self):
        if not self.check_env():
            return
        items = self.task_list.selectedItems()
        if not items:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_task_warn"))
            return
        for i in items:
            t = i.data(Qt.ItemDataRole.UserRole)
            t.status = "Waiting"
            t.set_rendered_frames(())
            self.start_param_extraction(t)
        self.refresh_ui()
        self.on_selection_changed()

    def on_custom_frames_changed(self, text):
        if not self.middle_panel.isEnabled():
            return
        has_text = bool(text.strip())
        if has_text:
            self.f_start.setText("")
            self.f_end.setText("")
            self.f_step.setText("")
            self.f_start.setEnabled(False)
            self.f_end.setEnabled(False)
            self.f_step.setEnabled(False)
        else:
            if self.current_task:
                self.f_start.setText(str(self.current_task.frame_start))
                self.f_end.setText(str(self.current_task.frame_end))
                self.f_step.setText(str(self.current_task.frame_step))
            is_locked = self.current_task and self.current_task.status in ["Rendering", "Completed"]
            if not is_locked:
                self.f_start.setEnabled(True)
                self.f_end.setEnabled(True)
                self.f_step.setEnabled(True)

    def validate_and_save_custom_frames(self):
        if not self.middle_panel.isEnabled() or not self.current_task:
            return
        text = self.custom_frames_edit.text().strip()
        if text:
            if not re.match(r'^(\d+\s*,\s*)*\d+\s*,?\s*$', text):
                self.append_log(self.tr("custom_frames_err_log").format(name=self.current_task.name))
        self.save_ui_to_task()

    def clear_custom_frames(self):
        if not self.middle_panel.isEnabled() or not self.current_task:
            return
        self.custom_frames_edit.setText("")
        self.validate_and_save_custom_frames()

    def auto_fill_missing_frames(self):
        if not self.middle_panel.isEnabled() or not self.current_task:
            return
        t = self.current_task
        out_path = self.out_path_edit.text().strip()
        if not out_path:
            QMessageBox.warning(self, self.tr("warning"), self.tr("no_output_path"))
            return

        start = t.frame_start
        end = t.frame_end
        step = t.frame_step

        dir_name = os.path.dirname(out_path)
        base_name = os.path.basename(out_path)

        missing_frames = []

        if not os.path.exists(dir_name):
            missing_frames = [str(f) for f in range(start, end + 1, step)]
        else:
            existing_frames = set()
            try:
                for file in os.listdir(dir_name):
                    if file.startswith(base_name):
                        suffix = file[len(base_name):]
                        match = re.match(r'^(\d+)', suffix)
                        if match:
                            existing_frames.add(int(match.group(1)))
            except Exception as e:
                self.append_log(f"读取输出目录失败: {str(e)}")
                return
            missing_frames = [str(f) for f in range(start, end + 1, step) if f not in existing_frames]

        if missing_frames:
            self.custom_frames_edit.setText(", ".join(missing_frames))
            self.validate_and_save_custom_frames()
            self.append_log(self.tr("log_auto_fill").format(name=t.name, count=len(missing_frames)))
        else:
            self.custom_frames_edit.setText("")
            self.validate_and_save_custom_frames()
            QMessageBox.information(self, self.tr("warning"), self.tr("no_missing_frames"))

    def check_error_detail(self, item):
        t = item.data(Qt.ItemDataRole.UserRole)
        if t.load_status == "Failed" or t.status == "Failed":
            error_info = getattr(t, 'error_msg', '')
            if not error_info:
                error_info = "Blender 进程意外终止或发生底层错误。\n👉 请查看软件界面右侧的【日志控制台】获取详细的崩溃报错！"
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(self.tr("error"))
            msg_box.setText(f"{self.tr('file')}: {t.name}\n\n{self.tr('reason')}:")
            msg_box.setDetailedText(error_info)
            msg_box.exec()

    def add_task_dialog(self):
        if not self.check_env():
            return
        fs, _ = QFileDialog.getOpenFileNames(self, self.tr("add_file"), "", "Blender (*.blend)")
        if fs:
            for f in fs:
                t = RenderTask(f)
                self.tasks.append(t)
                self.start_param_extraction(t)
            self.refresh_ui()

    def open_in_blender(self):
        if not self.check_env():
            return
        items = self.task_list.selectedItems()
        if not items:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_task_warn"))
            return
        launched = 0
        for i in items:
            t = i.data(Qt.ItemDataRole.UserRole)
            if os.path.exists(t.blend_path):
                try:
                    proc = subprocess.Popen([self.blender_path, t.blend_path])
                    # 登记为“用户自己打开的 Blender”：关闭本软件时不去动它
                    track_process(proc, detached=True)
                    launched += 1
                except Exception as e:
                    self.append_log(f"❌ 打开工程失败: {e}")
        if launched:
            self.append_log(f"已在 Blender 中打开 {launched} 个工程。")

    def start_param_extraction(self, task):
        task.load_status = "Loading"
        worker = ParamExtractorThread(self.blender_path, task)
        self.extractors.append(worker)
        worker.task_finished.connect(lambda: [self.refresh_ui(), self.on_selection_changed()])
        worker.finished.connect(lambda: self.extractors.remove(worker) if worker in self.extractors else None)
        worker.start()

    def save_ui_to_task(self):
        if not self.current_task or not self.middle_panel.isEnabled():
            return
        t = self.current_task
        t.scene_name = self.scene_cb.currentText()
        t.camera_name = self.camera_cb.currentText()
        try:
            t.resolution_x, t.resolution_y = int(self.res_x.text()), int(self.res_y.text())
        except Exception:
            pass
        try:
            t.frame_start, t.frame_end, t.frame_step = int(self.f_start.text()), int(self.f_end.text()), int(self.f_step.text())
        except Exception:
            pass
        t.output_path = self.out_path_edit.text()
        t.output_format = self.fmt_cb.currentText()
        t.custom_frames = self.custom_frames_edit.text().strip()
        if hasattr(self, 'indep_process_cb'):
            t.independent_process = self.indep_process_cb.isChecked()
        if hasattr(t, 'scene_data') and t.scene_name in t.scene_data:
            sd = t.scene_data[t.scene_name]
            sd['cc'] = t.camera_name
            sd['fs'] = t.frame_start
            sd['fe'] = t.frame_end
            sd['st'] = t.frame_step
            sd['rx'] = t.resolution_x
            sd['ry'] = t.resolution_y
            sd['out'] = t.output_path
            sd['fm'] = t.output_format
        self.save_session()

    def apply_cpu_affinity(self):
        if not HAS_PSUTIL:
            return
        pct = self.cpu_limit_cb.currentData()
        if pct is None:
            pct = 1.0

        for w in getattr(self, 'workers', []) or []:
            w.cpu_pct = pct
            if self.is_rendering and w.current_process:
                try:
                    pid = w.current_process.pid
                    p = psutil.Process(pid)
                    total_cores = psutil.cpu_count(logical=True)
                    cores_to_use = max(1, int(total_cores * pct))
                    p.cpu_affinity(list(range(cores_to_use)))
                except Exception:
                    pass

    def start_render(self):
        if not self.check_env():
            return

        valid_tasks = [t for t in self.tasks if t.load_status == "Success" and t.status in ["Waiting", "Failed", "Stopped"]]
        if not valid_tasks:
            QMessageBox.warning(self, self.tr("warning"),
                                "当前没有可执行的渲染任务！\n(如果需要重新渲染“已完成”的任务，请先在左侧选中它并点击【重置状态】)")
            return

        for task in valid_tasks:
            cf = getattr(task, 'custom_frames', '').strip()
            if cf:
                if not re.match(r'^(\d+\s*,\s*)*\d+\s*,?\s*$', cf):
                    QMessageBox.critical(self, self.tr("error"), self.tr("custom_frames_err_box").format(name=task.name))
                    return

        skipped_total = 0
        blind_tasks = []
        for task in valid_tasks:
            # 重新进入渲染队列时清掉上一次的错误信息，
            # 否则上一次失败过的任务这次渲染成功也会被标成“渲染出错”。
            task.error_msg = ""
            if task.status in ["Failed", "Stopped"]:
                task.status = "Waiting"

            # 输出目录里已经渲染好的帧，Blender 这次会直接跳过。
            # 不管是“停止后续渲”，还是重新导入工程/重置状态后再次开始，
            # 这些帧都必须计入总渲染进度，否则进度会一直停在 0%。
            existing = scan_existing_frames(task)
            if existing:
                task.set_rendered_frames(existing)
                skipped_total += len(existing)
            else:
                files, samples = inspect_output_dir(task)
                if files > 0:
                    blind_tasks.append((task.name, samples))

        if skipped_total > 0:
            self.append_log(self.tr("log_resume_progress").format(count=skipped_total))
        for name, samples in blind_tasks[:3]:
            self.append_log(self.tr("log_scan_failed").format(
                name=name, samples=", ".join(samples) if samples else "-"))

        if self.log_out.toPlainText().strip():
            self.log_out.append("\n\n" + "—" * 40 + "\n")

        self.is_rendering = True
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        self.btn_start.hide()
        self.btn_stop.show()
        # 进度条交给 update_stat 按“已渲染 / 总帧数”重新计算，重新开始时不再归零
        self.update_stat()
        self.batch_start_time = time.time()
        # 每个任务的计时在它真正开始渲染时（on_status_change）各自重置

        task_queue = queue.Queue()
        for t in valid_tasks:
            task_queue.put(t)

        max_parallel = self.parallel_cb.currentData() or 1
        num_workers = min(max_parallel, len(valid_tasks))

        self.workers = []
        self.active_workers = num_workers
        cpu_pct = self.cpu_limit_cb.currentData() or 1.0

        self.append_log(f"🚀 启动 {num_workers} 个并行渲染 worker，共 {len(valid_tasks)} 个任务。")

        for i in range(num_workers):
            w = RenderWorker(task_queue, self.blender_path)
            w.cpu_pct = cpu_pct
            w.status_updated.connect(self.on_status_change)
            w.log_updated.connect(self.filter_blender_log)
            w.frame_done.connect(self.on_frame_done)
            w.sample_updated.connect(self.update_frame_progress)
            w.worker_finished.connect(self.on_worker_finished)
            w.notice.connect(self.on_worker_notice)
            self.workers.append(w)

        for w in self.workers:
            w.start()

        self.frame_progress_bar.setValue(0)
        self.on_selection_changed()
        self.refresh_ui()

    def on_worker_finished(self):
        if getattr(self, '_exiting', False):
            return
        self.active_workers = getattr(self, 'active_workers', 1) - 1
        if self.active_workers <= 0:
            self.on_all_done()

    def on_worker_notice(self, tr_key):
        """worker 里的提示（以翻译键传递）。"""
        try:
            self.append_log(self.tr(tr_key))
        except Exception:
            pass

    def update_frame_progress(self, task, current, total, format_str=""):
        if format_str == "DENOISING":
            self.frame_progress_bar.setMaximum(1)
            self.frame_progress_bar.setValue(1)
            label = self.tr("denoising")
        else:
            self.frame_progress_bar.setMaximum(total)
            self.frame_progress_bar.setValue(current)
            if format_str.startswith("TILES:"):
                _, c_s, t_s, c_t, t_t = format_str.split(":")
                label = self.tr("frame_sample_tiled").format(c_s=c_s, t_s=t_s, c_t=c_t, t_t=t_t)
            else:
                label = self.tr("frame_sample")
        # 并行渲染时多个 worker 会轮流刷新同一根进度条，标注清楚这是哪个任务的采样
        if getattr(self, 'active_workers', 1) > 1:
            idx = 0
            try:
                idx = self.tasks.index(task) + 1
            except (ValueError, AttributeError):
                idx = 0
            if idx:
                label = self.tr("frame_task_prefix").format(idx=idx, text=label)
        self.frame_progress_bar.setFormat(label)

    def on_frame_done(self, task, real_frame_num):
        if getattr(self, '_exiting', False):
            return
        now = time.time()
        # 按任务分别计时：并行渲染时两个任务的帧会交替上报，
        # 用全局时间戳会把"别的任务的帧"算成这一帧的耗时（出现 0 秒/串台）。
        cost_seconds = int(round(task.note_frame_rendered(now)))
        time_str = self.format_time_str(cost_seconds)
        # 按帧号去重统计：磁盘上已存在（被 Blender 跳过）或之前已统计过的帧不会重复计数
        task.mark_frame_done(real_frame_num)

        task_idx = self.tasks.index(task) + 1
        frame_label = str(real_frame_num).strip() or str(getattr(task, 'rendered_frames', 0))
        msg = self.tr("log_frame_done").format(idx=task_idx, frame=frame_label, time_str=time_str)
        self.append_log(msg)
        self.update_stat()

        if hasattr(self, 'frame_progress_bar'):
            self.frame_progress_bar.setMaximum(1)
            self.frame_progress_bar.setValue(0)
            self.frame_progress_bar.setFormat(self.tr("frame_sample").replace('%v', '--').replace('%m', '--'))

        self.save_session()

    def parallel_stats(self):
        """并行渲染下的时间统计：当前最慢的一帧、正在渲染任务的平均单帧耗时。"""
        now = time.time()
        rendering = [t for t in self.tasks
                     if t.load_status == "Success" and t.status == "Rendering"]
        current = max((t.seconds_since_last_frame(now) for t in rendering), default=0.0)
        measured = [t.average_frame_time() for t in rendering if t.average_frame_time() > 0]
        if not measured:
            # 任务切换的空档（当前没有任务在渲染）时，退回全部已测到速度的任务
            measured = [t.average_frame_time() for t in self.tasks
                        if t.load_status == "Success" and t.average_frame_time() > 0]
        avg = sum(measured) / len(measured) if measured else 0.0
        return current, avg

    def estimate_remaining_seconds(self):
        """并行下的剩余时间估算：总工作量 / 并行数，且不小于最长任务的收尾时间。"""
        measured = [t.average_frame_time() for t in self.tasks
                    if t.load_status == "Success" and t.average_frame_time() > 0]
        if not measured:
            return None
        fallback = sum(measured) / len(measured)
        workers = max(1, int(getattr(self, 'active_workers', 1) or 1))

        total_work = 0.0
        longest_task = 0.0
        for t in self.tasks:
            if t.load_status != "Success" or t.status == "Completed":
                continue
            t_total = count_task_frames(t)
            left = max(0, t_total - min(getattr(t, 'rendered_frames', 0), t_total))
            if left <= 0:
                continue
            work = left * (t.average_frame_time() or fallback)
            total_work += work
            longest_task = max(longest_task, work)
        if total_work <= 0:
            return 0.0
        return max(total_work / workers, longest_task)

    def on_status_change(self, task_obj, status):
        if getattr(self, '_exiting', False):
            return
        task_obj.status = status
        if status == "Rendering":
            # 每个任务各自计时（并行时互不影响）
            task_obj.reset_timing()
            task_idx = self.tasks.index(task_obj) + 1
            msg = self.tr("log_task_start").format(idx=task_idx, name=task_obj.name, path=task_obj.output_path)
            self.append_log(msg)
        elif status == "Completed":
            started = getattr(task_obj, 'rendering_started_at', 0.0) or time.time()
            cost = time.time() - started
            msg = self.tr("log_task_done").format(name=task_obj.name, time_str=self.format_time_str(cost))
            self.append_log(msg)
        self.refresh_ui()
        self.on_selection_changed()
        self.save_session()

    def on_all_done(self):
        # 退出过程中绝不能再弹「渲染完成 -> 关机/重启」的确认框，那会挡住退出
        if getattr(self, '_exiting', False):
            return
        if not self.is_rendering:
            return
        self.is_rendering = False
        self.btn_start.show()
        self.btn_stop.hide()
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            pass

        rendered_task_count = sum(1 for t in self.tasks if getattr(t, 'rendered_frames', 0) > 0)
        total_frames = sum(getattr(t, 'rendered_frames', 0) for t in self.tasks)
        if total_frames > 0:
            total_cost = time.time() - getattr(self, 'batch_start_time', time.time())
            msg = self.tr("log_all_done").format(
                task_count=rendered_task_count,
                frame_count=total_frames,
                time_str=self.format_time_str(total_cost)
            )
            self.append_log(msg)

        action = self.after_render_action.currentData()
        if action != "None":
            action_tr = self.tr(action.lower())
            d = ActionConfirmDialog(action_tr, self, self.tr)
            if d.exec() == QDialog.DialogCode.Accepted:
                if action == "Shut Down":
                    subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
                elif action == "Restart":
                    subprocess.run(["shutdown", "/r", "/f", "/t", "0"])
        self.on_selection_changed()

    def stop_render(self):
        workers = list(getattr(self, 'workers', []) or [])
        for w in workers:
            w.is_running = False
            if w.current_rendering_task:
                w.current_rendering_task.status = "Stopped"

        # 并行、限时地结束子进程。
        # 以前是「每个 worker 各等 1.2s 优雅 + 各跑一遍 taskkill + 各 wait(2000)」，
        # 8 个并行任务叠起来能把界面冻住十几秒（用户只能去任务管理器强杀，
        # 而强杀一个正在收尾的进程恰好就是「拒绝访问」的来源）。
        deadline = time.time() + 2.5
        procs = [getattr(w, 'current_process', None) for w in workers]
        denied = stop_processes(procs, grace=0.3, force_timeout=1.5)

        # 兜底再确认一次（独立进程模式下 worker 可能刚好又拉起了一个 Blender）
        if time.time() < deadline:
            denied += stop_processes(
                [getattr(w, 'current_process', None) for w in workers],
                grace=0.0, force_timeout=max(0.2, deadline - time.time()))

        # 等 worker 线程收尾，但总共只等到 deadline，而不是每个都再等 2 秒
        for w in workers:
            left_ms = int(max(0.0, deadline - time.time()) * 1000)
            if left_ms <= 0:
                break
            try:
                w.wait(left_ms)
            except Exception:
                pass

        if denied:
            self.append_log("⚠️ 有进程拒绝被结束（PID: %s），可能已经卡在显卡驱动里。"
                            % sorted({int(p) for p in denied if p}))

        self.append_log(self.tr("log_stopped"))
        self.is_rendering = False
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            pass
        self.frame_progress_bar.setMaximum(1)
        self.frame_progress_bar.setValue(0)
        self.frame_progress_bar.setFormat(self.tr("frame_sample").replace('%v', '--').replace('%m', '--'))
        self.btn_start.show()
        self.btn_stop.hide()
        self.refresh_ui()
        self.on_selection_changed()
        self.save_session()

    def copy_task(self):
        items = self.task_list.selectedItems()
        for i in items:
            old_t = i.data(Qt.ItemDataRole.UserRole)
            nt = copy.deepcopy(old_t)
            nt.status = "Waiting"
            nt.set_rendered_frames(())
            self.tasks.append(nt)
        self.refresh_ui()
        self.save_session()

    def remove_task(self):
        items = self.task_list.selectedItems()
        for i in items:
            t = i.data(Qt.ItemDataRole.UserRole)
            if t in self.tasks:
                self.tasks.remove(t)
        self.refresh_ui()
        self.save_session()

    def clear_tasks(self):
        self.tasks.clear()
        self.refresh_ui()
        self.save_session()

    def select_blender_path(self):
        p, _ = QFileDialog.getOpenFileName(self, self.tr("blender_exe"), "", "Exec (*.exe)")
        if p:
            self.blender_path = p
            self.path_edit.setText(p)
            self.save_config()

    def select_output_path(self):
        p, _ = QFileDialog.getSaveFileName(self, self.tr("output"), self.out_path_edit.text())
        if p:
            self.out_path_edit.setText(p)

    def _config_payload(self):
        """把配置整理成纯数据（不含控件访问），GUI 线程取、后台线程写。"""
        return {
            "blender_path": self.blender_path,
            "current_lang": self.current_lang,
            "window_width": self.width(),
            "window_height": self.height(),
            "splitter_sizes": self.main_splitter.sizes() if hasattr(self, 'main_splitter') else [500, 600],
            "gpu_monitor": bool(getattr(self, 'gpu_monitor', True)),
        }

    def save_config(self):
        write_config_to_disk(self._config_payload())

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.blender_path = config_data.get('blender_path', "")
                self.current_lang = config_data.get('current_lang', "zh")
                # 显卡监控默认关闭：它要调 NVML/ADL，而显卡驱动一旦无响应，
                # 那个调用会永久卡在驱动里（这是「进程关不掉、只能重启」的实证成因）。
                # 想要显卡数字就在配置里写 "gpu_monitor": true。
                self.gpu_monitor = bool(config_data.get('gpu_monitor', False))
                self.path_edit.setText(self.blender_path)
                w = config_data.get('window_width', 1000)
                h = config_data.get('window_height', 800)
                self.resize(w, h)
                if 'splitter_sizes' in config_data and hasattr(self, 'main_splitter'):
                    self.main_splitter.setSizes(config_data['splitter_sizes'])
            except Exception:
                self.current_lang = "zh"
                self.blender_path = ""

    def count_existing_frames(self, task):
        """统计当前任务在磁盘上已经渲染好的帧数（用于“总渲染进度”）。
        只统计任务帧范围内的帧，所以换过输出目录 / 有其它文件也不会算错。"""
        return len(scan_existing_frames(task))

    def update_stat(self):
        total_frames = 0
        rendered_frames = 0
        completed_tasks = 0
        for t in self.tasks:
            if t.load_status == "Success":
                task_total_frames = count_task_frames(t)
                total_frames += task_total_frames
                if t.status == "Completed":
                    rendered_frames += task_total_frames
                    completed_tasks += 1
                else:
                    # 已渲染帧数按帧号去重，且不会超过任务总帧数
                    rendered_frames += min(getattr(t, 'rendered_frames', 0), task_total_frames)

        self.stat_label.setText(self.tr("total_frames_tip").format(
            total=total_frames,
            rendered=rendered_frames,
            count=len(self.tasks),
            completed=completed_tasks
        ))

        if hasattr(self, 'progress_bar'):
            if total_frames > 0:
                pct = min(100.0, rendered_frames / total_frames * 100)
                self.progress_bar.setValue(int(pct))
                # 帧数上万时整数百分比会长时间停在 0%，这里保留一位小数
                fmt = self.tr("total_progress")
                if "%p%" in fmt:
                    fmt = fmt.replace("%p%", f"{pct:.1f}")
                self.progress_bar.setFormat(fmt)
            else:
                self.progress_bar.setValue(0)

    def append_log(self, text):
        time_str = QTime.currentTime().toString('hh:mm:ss')
        self.log_out.append(f"【({time_str}) {text}】")

    def format_time_str(self, seconds):
        h, rem = divmod(int(seconds), 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}h{m:02d}m{s:02d}s"

    def filter_blender_log(self, line):
        clean_line = line.strip()
        if not clean_line:
            return
        if "Call `save()`" in clean_line or "Call save()" in clean_line:
            return
        if "Warning:" in clean_line or "Missing file" in clean_line or "not found" in clean_line.lower():
            self.append_log(self.tr("log_missing").format(detail=clean_line))
            return
        if clean_line.startswith("Error:") or clean_line.startswith("Exception:") or "RuntimeError" in clean_line:
            self.append_log(f"❌ [Blender 底层报错] 渲染可能已中断 -> {clean_line}")
            return
        if "Updating Scene" in clean_line or "Updating copy on write" in clean_line:
            return

    def get_gpu_info(self):
        """返回 (利用率字符串, 显存字符串)。

        只在第一次真正用到时才 nvmlInit()，之后一直复用，**不再每秒 nvmlShutdown()**：
        反复 Init/Shutdown 会反复加载 nvml.dll（诊断快照里那个进程的模块表就有
        两个 nvml.dll），而且 Shutdown 会打断别的线程正在进行的查询，属于典型的
        「自己把驱动往坏状态里推」的用法。
        """
        gpu_usage = "--"
        vram_str = "--"
        pynvml = _nvml_module()
        if pynvml is not None:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_usage = str(util.gpu)
                    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    used_gb = mem.used / (1024 ** 3)
                    total_gb = mem.total / (1024 ** 3)
                    vram_str = f"{used_gb:.1f}/{total_gb:.1f}G"
                return gpu_usage, vram_str
            except Exception:
                pass

        try:
            from pyadl import ADLManager
            devices = ADLManager.getInstance().getDevices()
            if devices:
                gpu_usage = str(devices[0].getUsage())
        except Exception:
            pass

        return gpu_usage, vram_str

    def poll_gpu_async(self):
        """在后台线程里取显卡信息，GUI 线程只读缓存。

        NVML / ADL 是直接和显卡驱动打交道的（内部有驱动锁 + ioctl）。
        一旦驱动卡住（刚强杀完正在吃 GPU 的 Blender、或者发生了 TDR），
        在 GUI 线程里调用就会把整个界面连同「关闭」一起冻住 —— 这正是
        「关不掉 + 只能重启」的一条典型成因。
        改成后台线程后，最坏情况也只是显卡数字不再刷新，界面和退出都不受影响。
        """
        if self._gpu_polling:
            # 上一次查询还没回来。超过 2 秒就认为「显卡驱动无响应」：
            # 这种调用会永久卡在驱动里，而一个卡在驱动里的线程足以让本进程
            # 永远停在「终止中」状态（之后任务管理器强杀就是「拒绝访问」）。
            # 所以这里永久停用显卡监控，不再往驱动里塞新的调用。
            started = getattr(self, '_gpu_poll_started_at', 0.0)
            if started and (time.time() - started) > 2.0 and not self._gpu_poll_slow:
                self._gpu_poll_slow = True
                with self._gpu_lock:
                    self._gpu_info = ("驱动无响应", "已停用")
                log_exit("显卡驱动查询超过 2s 未返回，已永久停用显卡监控（避免卡在驱动里）。")
            return
        if not getattr(self, 'gpu_monitor', False):
            return
        self._gpu_polling = True
        self._gpu_poll_started_at = time.time()

        def _job():
            try:
                info = self.get_gpu_info()
                with self._gpu_lock:
                    self._gpu_info = info
            except Exception:
                pass
            finally:
                self._gpu_polling = False

        try:
            threading.Thread(target=_job, daemon=True).start()
        except Exception:
            self._gpu_polling = False

    def current_gpu_info(self):
        with self._gpu_lock:
            return self._gpu_info

    def update_system_resources(self):
        if not self.isVisible():
            return
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.poll_gpu_async()
            gpu, vram = self.current_gpu_info()
            self.res_label.setText(self.tr("cpu_ram_usage").format(cpu=cpu, ram=ram, gpu=gpu, vram=vram))

        if hasattr(self, 'is_rendering') and self.is_rendering and hasattr(self, 'batch_start_time'):
            now = time.time()
            total_time = now - self.batch_start_time
            # 并行时这些数值按任务分别算：当前帧 = 最慢的那一帧，平均帧 = 各任务平均值，
            # 剩余时间 = 总工作量 / 并行数（不低于最长任务的收尾时间）
            current_seconds, avg_seconds = self.parallel_stats()
            eta_seconds = self.estimate_remaining_seconds()
            self.time_label.setText(self.tr("time_stats").format(
                total=self.format_time_str(total_time),
                current=self.format_time_str(current_seconds) if current_seconds > 0 else "--h--m--s",
                avg=self.format_time_str(avg_seconds) if avg_seconds > 0 else "--h--m--s",
                eta=self.format_time_str(eta_seconds) if eta_seconds is not None else "--h--m--s"
            ))
        else:
            self.time_label.setText(self.tr("time_stats").format(
                total="--h--m--s", current="--h--m--s", avg="--h--m--s", eta="--h--m--s"
            ))

    def check_env(self):
        if not self.blender_path or not os.path.exists(self.blender_path):
            QMessageBox.critical(self, self.tr("error"), self.tr("set_blender_first"))
            return False
        return True

    def block_signals(self, b):
        widgets = [
            self.scene_cb, self.camera_cb, self.fmt_cb, self.after_render_action,
            self.f_start, self.f_end, self.f_step, self.res_x, self.res_y,
            self.out_path_edit, self.custom_frames_edit,
        ]
        if hasattr(self, 'indep_process_cb'):
            widgets.append(self.indep_process_cb)
        for w in widgets:
            w.blockSignals(b)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()

    def dropEvent(self, e):
        if not self.check_env():
            return
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if p.endswith(".blend"):
                t = RenderTask(p)
                self.tasks.append(t)
                self.start_param_extraction(t)
        self.refresh_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)

    if socket.waitForConnected(500):
        socket.write(b"WAKE_UP")
        socket.flush()
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
        os._exit(0)

    local_server = QLocalServer()
    QLocalServer.removeServer(SERVER_NAME)
    local_server.listen(SERVER_NAME)
    _LOCAL_SERVER = local_server

    win = MainWindow()

    def on_new_connection():
        client_socket = local_server.nextPendingConnection()
        if client_socket:
            client_socket.waitForReadyRead(500)
            data = client_socket.readAll()
            if data == b"WAKE_UP":
                win.showNormal()
                win.activateWindow()
            client_socket.deleteLater()

    local_server.newConnection.connect(on_new_connection)

    win.show()
    sys.exit(app.exec())
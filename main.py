import subprocess
import threading
import queue
import time
from typing import Optional, Union, Tuple, List
from utils.clolorful_print import print_color
from utils.ges_init import connect_get_info, CommandExecutionProfile

# 定义队列用于线程间通信
output_queue = queue.Queue[str]()
shutdown = False  # 全局退出标志


def process_listener(
    process: subprocess.Popen,
    queue: queue.Queue[str],
    label: str,
    exit_string: Optional[str] = None
) -> None:
    """
    监听进程输出并放入队列
    :param process: 子进程对象
    :param queue: 输出队列
    :param label: 输出标签
    :param exit_string: 终止字符串(可选)
    """
    global shutdown
    try:
        while not shutdown:
            output = process.stdout.readline()
            if not output:
                break
            queue.put(f"{label} {output.strip()}")  # 标签+输出内容
            if exit_string and exit_string in output.strip():
                shutdown = True
                print(f"检测到终止字符串 '{exit_string}'，即将退出程序")
            time.sleep(0.1)
    finally:
        process.stdout.close()

def start_command_profiles(profiles: List[CommandExecutionProfile]) -> List[subprocess.Popen]:
    """
    启动多个命令配置并返回进程对象列表
    :param profiles: 命令配置列表
    :return: 子进程对象列表
    """
    global shutdown
    processes = []
    threads = []

    # 为每个配置启动进程和监听线程
    for profile in profiles:
        try:
            # 启动子进程
            process = subprocess.Popen(
                profile.cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # 行缓冲
            )
            processes.append(process)
            
            # 创建监听线程
            thread = threading.Thread(
                target=process_listener,
                args=(process, output_queue, profile.label, profile.terminal_string),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        except Exception as e:
            print_color(f"启动命令失败: {' '.join(profile.cmd_list)} | 错误: {e}", "RED")
            shutdown = True

    return processes

def main() -> None:
    global shutdown

    # 连接设备并获取信息
    device_id, width, height, orientation = connect_get_info()    
    print(f"设备ID: {device_id}, 分辨率: {width}x{height}, 方向: {orientation}")

    # 创建命令配置
    profiles = [
        CommandExecutionProfile(
            label="event",
            cmd_list=[
    "bash", "-c",     
    "date +'%H-%M-%S'; adb -s localhost:5555 shell \"getevent -lt | grep -E 'ABS_MT_TRACKING_ID|ABS_MT_POSITION_|KEY_VOLUMEUP         DOWN'\""
            ],
            terminal_string="KEY_VOLUMEUP",
            color="GREEN"
        ),
        CommandExecutionProfile(
            label="orientation",
            cmd_list=[
        'adb', 
        '-s', 'localhost:5555', 
        'shell', 
        """
while true; do
    cur=$(dumpsys window displays | grep init= | awk -F' ' '{
        split($1,a,"x");
        split($3,b,"x");
        if(a[2]==b[2]){print 1}else{print 0}
    }')
    if [ "$cur" != "$prev" ]; then
        time=$(date +'%H-%M-%S')
        echo "[DEBUG] 方向变化检测: 时间 $time, 前一个状态 prev: $prev, 当前状态 cur: $cur"
        prev=$cur
    fi
    sleep 1
done
""".strip()
    ],
            terminal_string=None,
            color="RED"
        )
    ]

    # 启动所有命令配置
    processes = start_command_profiles([profiles[0]])
    if not processes:
        return

    try:
        # 主循环处理队列输出
        while not shutdown:
            # 处理所有队列中的输出
            while not output_queue.empty():
                output = output_queue.get()
                label, _, content = output.partition(' ')
                
                # 查找匹配的配置进行彩色打印
                for profile in profiles:
                    if profile.label == label:
                        print_color(content, profile.color)
                        break
                else:  # 未找到匹配配置
                    print(output)

            # 检查所有进程是否已结束
            if all(p.poll() is not None for p in processes):
                shutdown = True
                print("所有子进程已结束")
                
            time.sleep(0.1)  # 避免CPU占用过高
            
    finally:
        # 清理资源
        for process in processes:
            try:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=2)
            except Exception as e:
                print(f"终止进程时出错: {e}")

if __name__ == "__main__":
    main()
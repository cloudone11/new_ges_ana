import subprocess
import threading
import queue
import time
from typing import Optional, Union, Tuple
from utils.clolorful_print import print_color
from utils.ges_init import connect_get_info
# 定义队列用于线程间通信
output_queue = queue.Queue[str]()

# 定义一个标志变量，用于控制程序的退出
shutdown = False

def process_listener(
    process: subprocess.Popen[str],
    queue: queue.Queue[str],
    label: str,
    exit_string: Optional[str] = None
) -> None:
    """
    监听进程的输出并将其放入队列。
    如果进程输出了特定字符串，则设置退出标志。
    """
    global shutdown
    try:
        while not shutdown:
            output = process.stdout.readline()
            if not output:
                break
            queue.put(label + " " + output.strip())  # 将输出放入队列
            if exit_string and output.strip().__contains__(exit_string.strip()):
                shutdown = True
                print(f"检测到进程输出特定字符串 '{exit_string.strip()}'，即将退出程序。")
    finally:
        process.stdout.close()

def main() -> None:
    global shutdown

    # 定义特定字符串，用于触发退出
    exit_string = "KEY_VOLUMEUP"
    labels = ["event", "orientation"]
    # 连接设备并获取信息
    device_id, width, height, orientation= connect_get_info()    
    print(f"设备ID: {device_id}, 分辨率: {width}x{height}, 方向: {orientation}")

    # 启动两个进程
    process1 = subprocess.Popen(
        [
    "bash", "-c",     
    "echo 1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    shell_script = """
echo 1;
""".strip()  # 去除首尾空白确保命令格式正确
    # 构建 Popen 命令列表
    _CMD = [
        'adb', 
        '-s', 'localhost:5555', 
        'shell', 
        shell_script
    ]
    process2 = subprocess.Popen(
         _CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # 创建监听线程
    thread1 = threading.Thread(
        target=process_listener,
        args=(process1, output_queue, labels[0], exit_string)
    )
    thread2 = threading.Thread(
        target=process_listener,
        args=(process2, output_queue, labels[1])
    )

    # 启动线程
    thread1.start()
    thread2.start()

    try:
        while not shutdown:
            # 从队列中获取数据
            while not output_queue.empty():
                output = output_queue.get()
                if output:
                    str1, str2 = output.split(' ', 1)
                    # 打印带颜色的输出
                    if str1 == labels[0]:
                        print_color(str2, "GREEN")
                    elif str1 == labels[1]:
                        print_color(str2, "RED")
                    else:
                        print(output)

            # 等待进程结束或触发退出
            if process1.poll() is not None and process2.poll() is not None:
                shutdown = True
                print("所有进程已结束。")
            time.sleep(0.1)  # 避免CPU占用过高
    finally:        

        # 关闭进程
        process1.terminate()
        process2.terminate()

        process1.stdout.close()
        process2.stdout.close()

        process1.wait()
        process2.wait()

        # 等待线程结束
        thread1.join()
        thread2.join()

if __name__ == "__main__":
    main()
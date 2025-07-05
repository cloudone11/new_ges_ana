from typing import Tuple, List
import subprocess

# 定义全局变量控制是否打印
PRINT_DEBUG = False  # 设置为 True 打印，设置为 False 不打印

def print_debug(message: str):
    """
    根据全局变量 PRINT_DEBUG 决定是否打印调试信息
    """
    if PRINT_DEBUG:
        print(message)

def connect_get_info() -> Tuple[str, int, int, str]:
    """
    获取设备id，屏幕分辨率和方向。在未连接设备时会尝试连接一次，连接失败返回"0",0,0,"0"。
    """
    print_debug("连接设备并获取信息...")
    device_id = ""
    width = ""
    height = ""
    orientation = ""
    result = subprocess.run("adb devices -l | grep localhost:5555;", shell=True, text=True, capture_output=True)
    if result.stdout:
        print_debug("已连接。设备信息： ")
        device_id = result.stdout.split("device product:")[1].split(" ")[0]
        print_debug(f"设备ID: {device_id}")
    else:
        print_debug("未检测到设备。尝试连接一次。")
        result = subprocess.run("adb connect localhost:5555", shell=True, text=True, capture_output=True)
        if result.stdout:
            print_debug(f"连接成功: {result.stdout.strip()}")
            result = subprocess.run("adb devices -l | grep localhost:5555;", shell=True, text=True, capture_output=True)
            if result.stdout:
                print_debug("成功连接。设备信息： ")
                device_id = result.stdout.split("device product:")[1].split(" ")[0]
                print_debug(f"设备ID: {device_id}")
        else:
            print_debug(f"尝试连接失败: {result.stderr.strip()}")
            return "0", 0, 0, "0"

    cmd = '''
adb -s localhost:5555 shell "dumpsys window displays | grep init=" | awk -F' ' '{
    print $1;
}';
'''

    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.stdout:
        width, height = result.stdout.split("=", 1)[1].split("x")
        width = int(width.strip())
        height = int(height.strip())
        print_debug(f"屏幕分辨率: {width}x{height}")
    if result.stderr:
        print_debug(f"Error: {result.stderr}")

    cmd = '''
adb -s localhost:5555 shell "dumpsys window displays | grep init=" | awk -F' ' '{
    # 分割 $1 和 $4
    split($1, a, "x");
    split($3, b, "x");

    # 判断逻辑
    if (a[2] == b[2]) {
        print 1;
    } else {
        print 0;
    }
}';
'''
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.stdout:
        if result.stdout.strip() == "1":
            print_debug("设备方向为竖屏。")
            orientation = "竖屏"
        elif result.stdout.strip() == "0":
            print_debug("设备方向为横屏。")
            orientation = "横屏"
        else:
            print_debug("获取设备方向时超出预期： ", result.stdout.strip())

    return device_id, width, height, orientation


class CommandExecutionProfile:
    def __init__(self, label: str, cmd_list: List[str], terminal_string: str, color: str):
        """
        初始化对象
        :param label: 标签字符串
        :param cmd_list: 命令字符串列表
        :param terminal_string: 终端字符串
        :param color: 颜色字符串
        """
        if not isinstance(label, str):
            raise TypeError("label must be a string")
        if not isinstance(cmd_list, list) or not all(isinstance(item, str) for item in cmd_list):
            raise TypeError("cmd_list must be a list of strings")
        if not isinstance(terminal_string, str):
            raise TypeError("terminal_string must be a string")
        if not isinstance(color, str):
            raise TypeError("color must be a string")

        self.label = label
        self.cmd_list = cmd_list
        self.terminal_string = terminal_string
        self.color = color

    def __str__(self):
        """
        返回对象的字符串表示
        """
        return (f"Label: {self.label}\n"
                f"CMD List: {self.cmd_list}\n"
                f"Terminal String: {self.terminal_string}\n"
                f"Color: {self.color}")




# 示例用法
if __name__ == "__main__":
    # 创建一个对象实例
    obj = CommandExecutionProfile(
        label="Example Label",
        cmd_list=["bash", "-c", "echo 'Hello, World!'"],
        terminal_string="xterm",
        color="blue"
    )

    # 访问属性
    print("Label:", obj.label)
    print("CMD List:", obj.cmd_list)
    print("Terminal String:", obj.terminal_string)
    print("Color:", obj.color)

    # 打印对象的完整信息
    print("\nObject Details:")
    print(obj)
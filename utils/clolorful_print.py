# 定义颜色字典
COLORS = {
    "RED": "\033[91m",    # 红色
    "GREEN": "\033[92m",  # 绿色
    "YELLOW": "\033[93m", # 黄色
    "BLUE": "\033[94m",   # 蓝色
    "RESET": "\033[0m"    # 重置颜色
}

def print_color(text, color):
    """
    打印带有颜色的文本。
    
    :param text: 要打印的文本
    :param color: 颜色名称（如 "RED", "GREEN", "YELLOW", "BLUE"）
    """
    if color in COLORS:
        print(COLORS[color] + text + COLORS["RESET"])
    else:
        print("未知颜色：", color)
        print(text)
if __name__ == "__main__":
    # 使用示例
    print_color("这是红色文字", "RED")
    print_color("这是绿色文字", "GREEN")
    print_color("这是黄色文字", "YELLOW")
    print_color("这是蓝色文字", "BLUE")
import subprocess
import sys
import os

def run_script_and_process_output():
    # 根据平台选择执行方式
    if sys.platform == 'win32':
        # Windows平台使用cmd.exe执行
        process = subprocess.Popen(
            ['cmd.exe', '/c', 'test.bat'],  # 假设已创建test.bat
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=os.getcwd()  # 使用当前工作目录
        )
    else:
        # Linux/Mac平台使用sh执行
        process = subprocess.Popen(
            ['sh', 'test.sh'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=os.getcwd()
        )
    
    # 逐行处理标准输出
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if line:  # 忽略空行
            print(f"处理输出: {line}")
            # 这里可以添加自定义处理逻辑
    
    # 处理标准错误
    stderr_output = process.stderr.read()
    if stderr_output:
        print(f"错误输出: {stderr_output}")
    
    # 等待进程结束
    return_code = process.wait()
    print(f"进程结束，返回码: {return_code}")

if __name__ == "__main__":
    run_script_and_process_output()

#!/bin/bash

# 全局配置
IP="localhost"           # 设备IP
PORT="5555"              # 设备端口
OUTPUT_FILE="./test.txt"  # 输出文件路径
DEVICE="${IP}:${PORT}"   # 设备地址

# 创建目录（如果不存在）
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 检查设备是否已连接
check_device() {
    adb devices -l | grep "$DEVICE"
}

# 尝试连接设备
try_connect() {
    echo "设备未连接，尝试连接..."
    adb connect "$DEVICE"
    
    # 等待最多60秒，每秒检查一次
    local timeout=60
    local start_time=$(date +%s)
    
    while true; do
        if check_device > /dev/null; then
            echo "设备连接成功"
            return 0
        fi
        
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge $timeout ]; then
            echo "连接超时（60秒），退出脚本"
            return 1
        fi
        
        sleep 1
    done
}

# 获取屏幕信息
get_screen_info() {
    echo "获取屏幕信息..."
    adb -s "$DEVICE" shell "dumpsys window displays | grep init=" | awk -F' ' '{print $1}' > "$OUTPUT_FILE"
    date +'%H-%M-%S' >> "$OUTPUT_FILE"
}

# 检测方向变化（后台运行）
monitor_rotation() {
    echo "启动方向变化监控..."
    adb -s "$DEVICE" shell "
    prev=\"\"
    while true; do
        # 获取当前方向状态
        cur=\$(dumpsys window displays | grep init= | awk -F' ' '{
            split(\$1,a,\"x\");
            split(\$3,b,\"x\");
            if(a[2]==b[2]){print 1}else{print 0}
        }')

        # 检测方向变化
        if [ \"\$cur\" != \"\$prev\" ]; then
            time=\$(date +'%H-%M-%S')
            echo \"[DEBUG] 方向变化检测: 时间 \$time, 前一个状态 prev: \$prev, 当前状态 cur: \$cur\"
            prev=\$cur
        fi
        sleep 1
    done" >> "$OUTPUT_FILE" &
    ROTATION_PID=$!
}

# 检测手势事件（后台运行）
monitor_touch() {
    echo "启动手势监控..."
    adb -s "$DEVICE" shell "getevent -lt | grep -E 'ABS_MT_TRACKING_ID|ABS_MT_POSITION_|KEY_VOLUMEUP.*DOWN'" >> "$OUTPUT_FILE" &
    TOUCH_PID=$!
}

# 清理函数
cleanup() {
    echo "清理后台进程..."
    kill $ROTATION_PID 2>/dev/null
    kill $TOUCH_PID 2>/dev/null
    adb kill-server
}

# 主函数
main() {
    # 检查设备连接
    if ! check_device > /dev/null; then
        try_connect || exit 1
    fi

    # 执行监控任务
    get_screen_info
    monitor_rotation
    monitor_touch

    # 等待用户输入q退出
    echo "监控已启动，输入 q 回车 或按 Ctrl+C 停止..."
    while true; do
        # 使用read -t 0.1实现非阻塞读取
        read -t 0.1 input
        if [[ "$input" == "q" ]]; then
            echo "检测到输入 q，准备退出..."
            cleanup
            exit 0
        fi
        # 短暂睡眠减少CPU占用
        sleep 0.5
    done
}

# 执行主函数
main
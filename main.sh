#!/bin/bash

# 定义文件路径
OUTPUT_FILE="./test.txt"

# 创建目录（如果不存在）
mkdir -p "$(dirname "$OUTPUT_FILE")"

# 检查设备是否已连接
check_device() {
    adb devices -l | grep "localhost:5555"
}

# 尝试连接设备
try_connect() {
    echo "设备未连接，尝试连接..."
    adb connect localhost:5555
    
    # 等待最多60秒，每秒检查一次
    local timeout=60
    local start_time=$(date +%s)
    
    while true; do
        if check_device > /dev/null; then
            echo "设备连接成功"
            check_device > "$OUTPUT_FILE"
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

# 主逻辑
if check_device > /dev/null; then
    echo "设备已连接"
    check_device > "$OUTPUT_FILE"
else
    try_connect || exit 1
fi

echo "操作完成"
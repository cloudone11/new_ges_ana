# 在安卓设备中存放于/sdcard/shell/test.sh 中，甲壳虫adb使用命令：
# cd /sdcard/shell/; sh test.sh
# 失败：adb不可用
# 获取设备信息
adb devices -l | grep localhost:5555 >/sdcard/shell/test.txt;
# 获取屏幕信息
adb -s localhost:5555 shell "dumpsys window displays | grep init=" | awk -F' ' '{
    print $1;
}' >/sdcard/shell/test.txt;
date +'%H-%M-%S' >/sdcard/shell/test.txt;
# 获取方向变化

adb -s localhost:5555 shell "
while true; do
    # 获取当前方向状态
    cur=\$(dumpsys window displays | grep init= | awk -F' ' '{
        split(\$1,a,\"x\");
        split(\$3,b,\"x\");
        if(a[2]==b[2]){print 1}else{print 0}
    }');

    # 检测方向变化
    if [ \"\$cur\" != \"\$prev\" ]; then
        time=\$(date +'%H-%M-%S');
        echo \"[DEBUG] 方向变化检测: 时间 \$time, 前一个状态 prev: \$prev, 当前状态 cur: \$cur\"
        prev=\$cur;
    fi;

    sleep 1;
done" >/sdcard/shell/test.txt&

# 获取手势信息
adb -s localhost:5555 shell "getevent -lt | grep -E 'ABS_MT_TRACKING_ID|ABS_MT_POSITION_|KEY_VOLUMEUP         DOWN'" >/sdcard/shell/test.txt&
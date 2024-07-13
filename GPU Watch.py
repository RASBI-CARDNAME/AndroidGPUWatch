import subprocess
import time
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# ADB 커맨드 함수
def run_adb_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr

# 정지 버튼 클릭 시
def stop_update(event):
    global running
    running = False
    plt.close()

# 일시 정지 버튼 클릭 시
def pause_update(event):
    global paused
    paused = not paused
    if paused:
        btn_pause.label.set_text('Resume')
    else:
        btn_pause.label.set_text('Pause')

            
# 그래프 초기화
plt.ion()  # 인터랙티브 모드 활성화
fig, ax = plt.subplots(num = 'GPU Watch') #창이름
temp_values = []
clock_values = []
time_values = []

running = True
paused = False

# 정지 버튼
ax_stop = plt.axes([0.05, 0.90, 0.1, 0.075])
btn_stop = Button(ax_stop, 'Exit')
btn_stop.on_clicked(stop_update)

# 일시 정지 버튼
ax_pause = plt.axes([0.20, 0.90, 0.1, 0.075])
btn_pause = Button(ax_pause, 'Pause')
btn_pause.on_clicked(pause_update)

##메인 코드
try:
    while running:
        if not paused:
            command = 'adb shell su -c "cat /sys/class/kgsl/kgsl-3d0/gpuclk"'
            stdout, stderr = run_adb_command(command)

            if stderr:
                print("Error:", stderr)
            else:
                gpu_clock = float(stdout.strip()) / 1000000 #MHz로 변환
                clock_values.append(gpu_clock)

            
            command = f'adb shell su -c "cat /sys/class/kgsl/kgsl-3d0/temp"'
            stdout, stderr = run_adb_command(command)

            if stderr:
                print("Error:", stderr)
            else:
                gpu_temp = float(stdout.strip()) / 1000  # ℃로 변환
                temp_values.append(gpu_temp)

            time_values.append(len(time_values) + 1)

            # 그래프 업데이트
            ax.clear()
            ax.plot(time_values, temp_values, label='GPU T-die Temp (℃)')
            ax.plot(time_values, clock_values, label='GPU Clock (MHz)')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Value')
            ax.legend()

           # 수치 출력
            if len(temp_values) > 0:
                ax.text(0.02, 0.95, f'GPU Temp: {temp_values[-1]:.2f} ℃', transform=ax.transAxes, fontsize=12, va='top')
            if len(clock_values) > 0:
                ax.text(0.02, 0.85, f'GPU Clock: {clock_values[-1]:.2f} MHz', transform=ax.transAxes, fontsize=12, va='top')
        
        plt.pause(1)  # 1초마다 업데이트
    
except KeyboardInterrupt:
    print("그래프 표시를 종료합니다.")

plt.ioff()
plt.show()

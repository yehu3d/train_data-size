import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import time
import os
import numpy as np

# 需要绘制的最新数据点数
sss = 5000
avg_window_size = 20  # 可以调整滑动窗口的大小

# 初始化数据存储
p0loss_data = []
vloss_data = []
pacc1_data = []
loss_data = []  # 新增：loss 数据列表

# 记录文件的读取位置
last_position = 0

# 设置绘图：将原先的 3 行子图扩展为 4 行子图
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 16))

# 设置标题与坐标轴标签
ax1.set_title("Real-time p0loss")
ax1.set_xlabel("Iterations")
ax1.set_ylabel("p0loss")
ax1.grid(True)  # 启用网格
 
ax2.set_title("Real-time vloss")
ax2.set_xlabel("Iterations")
ax2.set_ylabel("vloss")
ax2.grid(True)  # 启用网格
 
ax3.set_title("Real-time pacc1")
ax3.set_xlabel("Iterations")
ax3.set_ylabel("pacc1")
ax3.grid(True)  # 启用网格
 
ax4.set_title("Real-time loss")  # 新增：loss
ax4.set_xlabel("Iterations")
ax4.set_ylabel("loss")
ax4.grid(True)  # 启用网格

# 创建四条线条
line_p0loss, = ax1.plot([], [], label="p0loss", color='r')
line_vloss,  = ax2.plot([], [], label="vloss",  color=(0, 0, 1, 0.6))  # 修改：将蓝色设置为透明
line_pacc1,  = ax3.plot([], [], label="pacc1",  color=(0, 1, 0, 0.8))
line_loss,   = ax4.plot([], [], label="loss",   color='m')  # 新增：loss 线条

# 创建四条滑动平均线条（颜色改为黑色）
line_p0loss_avg, = ax1.plot([], [], label="p0loss_avg", color='black', linestyle='-', linewidth=3)
line_vloss_avg,  = ax2.plot([], [], label="vloss_avg", color='black', linestyle='-', linewidth=3)
line_pacc1_avg,  = ax3.plot([], [], label="pacc1_avg", color='black', linestyle='-', linewidth=3)
line_loss_avg,   = ax4.plot([], [], label="loss_avg", color='black', linestyle='-', linewidth=3)

def moving_average(data, window_size):
    """
    计算滑动平均
    """
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def read_log_file(filename):
    """
    读取日志文件中的新增数据，并更新全局的 p0loss_data、vloss_data、pacc1_data、loss_data。
    """
    global last_position, p0loss_data, vloss_data, pacc1_data, loss_data
    
    with open(filename, 'r') as file:
        # 跳到上次读取的位置
        file.seek(last_position)
        lines = file.readlines()
        
        for line in lines:
            # 分别匹配 p0loss, vloss, pacc1, loss
            p0loss_match = re.search(r"\bp0loss\s*=\s*([\d\.]+)", line)
            vloss_match  = re.search(r"\bvloss\s*=\s*([\d\.]+)",  line)
            pacc1_match  = re.search(r"\bpacc1\s*=\s*([\d\.]+)",  line)
            loss_match   = re.search(r"\bloss\s*=\s*([\d\.]+)",   line)

            
            # 若匹配到，则追加到各自数据列表中
            if p0loss_match:
                p0loss_data.append(float(p0loss_match.group(1)))
            if vloss_match:
                vloss_data.append(float(vloss_match.group(1)))
            if pacc1_match:
                pacc1_data.append(float(pacc1_match.group(1)))
            if loss_match:
                loss_data.append(float(loss_match.group(1)))

        # 更新文件的读取位置
        last_position = file.tell()

def update_plot(frame, n):
    """
    update_plot 函数会在动画中被循环调用。
    每次被调用前，会先从日志文件中读入最新数据，然后只取最新的 n 条进行绘图。
    """
    # 每次更新前，读取新增数据
    read_log_file('stdout.txt')

    # 当前所有数据的长度
    length_p0loss = len(p0loss_data)
    length_vloss  = len(vloss_data)
    length_pacc1  = len(pacc1_data)
    length_loss   = len(loss_data)

    # 确保 n 不超过四者中的最小长度
    # 若你的日志中，有些量可能比另一些量更新得更快或更慢，可以做一些额外判断
    min_len = min(length_p0loss, length_vloss, length_pacc1, length_loss)
    n = min(n, min_len)

    # 只取最新的 n 条数据
    p0loss_latest = p0loss_data[-n:]
    vloss_latest  = vloss_data[-n:]
    pacc1_latest  = pacc1_data[-n:]
    loss_latest   = loss_data[-n:]

    # 横坐标
    start_index = min_len - n
    x_values = range(start_index, start_index + n)

    # 设置线条数据
    line_p0loss.set_data(x_values, p0loss_latest)
    line_vloss.set_data(x_values, vloss_latest)
    line_pacc1.set_data(x_values, pacc1_latest)
    line_loss.set_data(x_values, loss_latest)

    # 计算滑动平均（可以调整窗口大小）
    p0loss_avg = moving_average(p0loss_latest, avg_window_size)
    vloss_avg  = moving_average(vloss_latest, avg_window_size)
    pacc1_avg  = moving_average(pacc1_latest, avg_window_size)
    loss_avg   = moving_average(loss_latest, avg_window_size)

    # 设置滑动平均线数据
    line_p0loss_avg.set_data(x_values[:len(p0loss_avg)], p0loss_avg)
    line_vloss_avg.set_data(x_values[:len(vloss_avg)], vloss_avg)
    line_pacc1_avg.set_data(x_values[:len(pacc1_avg)], pacc1_avg)
    line_loss_avg.set_data(x_values[:len(loss_avg)], loss_avg)

    # 调整显示范围
    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()
    ax3.relim()
    ax3.autoscale_view()
    ax4.relim()
    ax4.autoscale_view()

    # 在控制台输出最新一条信息（可根据需要选择是否保留）
    if n > 0:
        print(f"Update complete! "
              f"Last p0loss: {p0loss_latest[-1]}, "
              f"Last vloss: {vloss_latest[-1]}, "
              f"Last pacc1: {pacc1_latest[-1]}, "
              f"Last loss: {loss_latest[-1]}")

    # 返回这几条线，便于 FuncAnimation 进行更新
    return (line_p0loss, line_vloss, line_pacc1, line_loss,
            line_p0loss_avg, line_vloss_avg, line_pacc1_avg, line_loss_avg)

def animate(n):
    """
    animate 函数主要用于启动动画。
    interval=1000 表示每 1 秒更新一次。
    fargs=(n,) 中传入的 n，即表示最新绘制多少条数据。
    """
    ani = animation.FuncAnimation(
        fig,                 # 画布
        update_plot,         # 更新函数
        fargs=(n,),          # 传给更新函数的额外参数
        interval=1000,       # 1000ms 更新一次
        blit=True            # blit=True 提高绘制效率
    )
    plt.tight_layout()
    plt.show()

# 调用 animate 函数，指定要绘制的数据点数（例如 4000）
animate(sss)

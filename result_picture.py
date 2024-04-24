import matplotlib.pyplot as plt

# 读取数据
file_path1 = "package_loss_normal_o.txt"
file_path2 = "package_loss_normal.txt"

with open(file_path1, 'r') as file1, open(file_path2, 'r') as file2:
    data1 = [float(line.strip()) for line in file1.readlines()]
    data2 = [float(line.strip()) for line in file2.readlines()]

# 计算最小长度
min_length = min(len(data1), len(data2))

# 截取数据，使其长度相同
data1 = data1[:min_length]
data2 = data2[:min_length]

# 创建一个新的图表
plt.figure()

# 画出第一个数据集的折线
plt.plot(data1, label='constant', marker='o')

# 画出第二个数据集的折线
plt.plot(data2, label='Adaptive', marker='o')

# 添加图例
plt.legend(fontsize=15)

# 横纵坐标label
plt.xlabel('total packet number', fontsize=10)
plt.ylabel('packet loss rate', fontsize=10)

# 调整标题和图例之间的垂直间隔
plt.subplots_adjust(top=0.9)

plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

# 显示网格
plt.grid(True)

# 显示图表
plt.show()

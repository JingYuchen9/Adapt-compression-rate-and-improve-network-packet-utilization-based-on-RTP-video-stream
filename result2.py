import matplotlib.pyplot as plt

# 读取数据
with open('package_total_o.txt', 'r') as file_o:
    data_o = [int(line.strip()) for line in file_o]

with open('package_total.txt', 'r') as file:
    data = [int(line.strip()) for line in file]

# 计算数据总和
total_o = sum(data_o)
total = sum(data)

# 设置标签
labels = ['', '']

# 设置饼图的大小
plt.figure(figsize=(8, 8))

# 画饼图，并设置标签和百分比的字体大小
plt.pie([total_o, total], labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 20})

# 设置图表标题
# plt.title('Data packets consumed(network resources) when transmitting the same video in two ways')

plt.legend(['Traditional data segmentation', 'Optimized data segmentation'], fontsize=10)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)

# 显示网格
plt.grid(True)

# 显示图表
plt.show()


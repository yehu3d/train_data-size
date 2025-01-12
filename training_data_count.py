import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 请求目标网页
url = 'https://katagoarchive.org/kata1/trainingdata/index.html'  # 替换为实际的网站 URL
response = requests.get(url)
html_content = response.text

# 解析网页内容
soup = BeautifulSoup(html_content, 'html.parser')

# 查找所有的 <a> 标签，假设每个文件信息的大小和日期都包含在 <a> 标签的同一行
file_entries = soup.find_all('a')

# 计算从指定时间段内的总文件大小
total_size_mb = 0
start_date = datetime(2023, 6, 13)  # 修改为你要筛选的起始日期
cutoff_date = datetime(2026, 7, 31)  # 修改为你要筛选的截止日期

# 开关：默认关闭，开启才统计 start_date 到 cutoff_date 之间的数据
enable_date_filter = 0

for entry in file_entries:
    # 提取上一个兄弟节点的文本，获取文件大小
    size_str = entry.previous_sibling
    if size_str:
        size_str = size_str.strip().replace('\xa0', '')  # 去掉不可见字符，例如不间断空格

        # 判断单位是 MB 或 GB，并转换为 MB
        size_mb = 0
        if size_str.startswith("[") and size_str.endswith("M]"):
            try:
                size_mb = int(size_str[1:-2].strip())  # 去掉括号和 'M'，转换为整数
            except ValueError:
                continue  # 如果转换失败，跳过此行
        elif size_str.startswith("[") and size_str.endswith("G]"):
            try:
                size_gb = float(size_str[1:-2].strip())  # 去掉括号和 'G'，转换为浮点数
                size_mb = size_gb * 1024  # 将 GB 转换为 MB
            except ValueError:
                continue  # 如果转换失败，跳过此行

        # 提取日期
        date_str = entry.get('href').split('/')[-1][:10]  # 从 href 提取前 10 个字符作为日期
        #print(date_str)
        try:
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            continue  # 如果日期格式不对，跳过此行

        # 如果开关开启并且日期在指定的时间段内，累加文件大小
        if enable_date_filter:
            if start_date <= file_date <= cutoff_date:
                total_size_mb += size_mb
        else:
            if file_date >= start_date:
                total_size_mb += size_mb

# 将总大小从 MB 转换为 GB
total_size_gb = total_size_mb / 1024

# 获取当前时间
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 输出结果，包含起始日期和截止日期信息
if enable_date_filter:
    print(f"[{current_time}] 从 {start_date.strftime('%Y-%m-%d')} 到 {cutoff_date.strftime('%Y-%m-%d')} 之间文件的总大小是 {total_size_gb:.2f} GB")
else:
    print(f"[{current_time}] 从 {start_date.strftime('%Y-%m-%d')} 之后文件的总大小是 {total_size_gb:.2f} GB")

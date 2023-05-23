import os
import threading
import time
import requests

# Define the two tasks
transmission_host = os.environ.get('TRHOST')

def run_tracker_script():
    while True:
        # 从 links.txt 文件中读取链接列表
        with open('links.txt', 'r') as f:
            links = [line.strip() for line in f]

        # 定义一个列表用于存储旧文件中的行
        old_lines = []

        # 尝试读取文件 tracker.txt 中的所有行
        try:
            with open('tracker.txt', 'r') as f:
                old_lines = [line.strip() for line in f]
        except FileNotFoundError:
            pass  # 如果文件不存在，则忽略错误

        # 定义一个集合用于去重行
        line_set = set()

        # 循环遍历链接列表
        for link in links:
            # 发送 GET 请求并获取响应内容
            response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
            print(response)
            tracker_content=""
            if response.status_code == 200:
                tracker_content = response.text

            # 将响应内容按行分割，然后将所有行添加到集合中
            lines = tracker_content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    line_set.add(line)

        # 找出新增的行和已经存在的行
        new_lines = sorted(line_set - set(old_lines))
        dup_lines = sorted(line_set & set(old_lines))

        # 将新增的行写入文件，每行一个
        with open('tracker.txt', 'a') as f:
            for line in new_lines:
                f.write(line + '\n')

        # 输出哪些行是新增的
        if len(new_lines) > 0:
            print(f"Added {len(new_lines)} new line(s):")
            for line in new_lines:
                print(f"+ {line}")
        else:
            print("No new lines added.")

        # 输出哪些行已经存在于旧文件中
        if len(dup_lines) > 0:
            print(f"Found {len(dup_lines)} duplicate line(s):")
            # for line in dup_lines:
            #     print(f"- {line}")
        else:
            print("No duplicate lines found.")
        # Modify this to match your environment
        # Assumes that the tracker.py script is in the same directory as this script
        time.sleep(12 * 60 * 60) # sleep for 12 hours before running the tasks again


def update_tracker_for_all_torrents():
    while True:
        os.system("transmission-remote {} -l > list.txt".format(transmission_host))
        with open("list.txt", "r") as f:
            for line in f.readlines():
                fields = line.split()
                if len(fields) < 9 or fields[0] == "Sum:":
                    continue
                torrent_id = fields[0].strip()
                add_all_tracker_fortorrent(torrent_id)
        time.sleep(10 * 60) # sleep for 10 minutes before running the tasks again

# Use threading to run the tasks in parallel
def add_all_tracker_fortorrent(torrent_id):
    with open("tracker.txt", "r") as f:
        tracker_list = f.read().strip().split("\n")
        for tracker_url in tracker_list:
            os.system("transmission-remote {} -t {} -td '{}'".format(transmission_host,torrent_id,tracker_url))

if __name__ == '__main__':

    t1 = threading.Thread(target=run_tracker_script)
    t2 = threading.Thread(target=update_tracker_for_all_torrents)

    t1.start()
    t2.start()


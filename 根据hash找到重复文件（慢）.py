import os
import hashlib
from collections import defaultdict

def find_duplicate_files(folder_path):
    """
    遍历指定文件夹及其子文件夹，比较MD5查找重复文件

    Args：
        folder_path(str): 需要便利的文件夹路径
    
    Returns：
        dict：字典
    """
    if not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}'不是一个有效的文件夹路径。")
        return {}
    
    md5_map = defaultdict(list)
    print("正在扫描文件...")

    for root, _, files in os.walk(folder_path):
        for filename in files:
            # 过滤掉 .DS_Store 和其他隐藏的系统文件
            if filename == ".DS_Store":
                continue

            print(f"扫描到文件: {filename}")

            file_path = os.path.join(root, filename)
            #跳过软链接，防止无限循环
            if not os.path.islink(file_path):
                try:
                    #计算MD5指
                    with open(file_path, 'rb') as f:
                        md5 = hashlib.md5(f.read()).hexdigest()
                    md5_map[md5].append(file_path)
                except Exception as e:
                    print(f"无法处理文件{file_path}: {e}")
    duplicate_files = {md5: paths for md5, paths in md5_map.items() if len(paths) > 1}
    return duplicate_files

def print_duplicate_files(duplicates):
    """
    打印重复文件信息
    """
    if not duplicates:
        print("没有找到重复文件。")
        return 
    print("\n找到以下重复文件：")
    for md5, paths in duplicates.items():
        print(f"\nMD5:{md5}")
        for path in paths:
            print(f"- {path}")
        print("-" * 20)

if __name__ == "__main__":
    # 替换成需要扫描的文件夹路径
    target_folder = "/Volumes/STORE/sex_files/tg"

    # 获取重复文件列表
    found_duplicates = find_duplicate_files(target_folder)

    # 打印结果
    print_duplicate_files(found_duplicates)
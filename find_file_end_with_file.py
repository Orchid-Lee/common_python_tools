import os

"""
查找文件夹及其子文件夹，找到以'_file'结尾的文件，并输出路径

Args:
    folder_path(str): 要遍历的根目录路径
    suffix(str): 要查找的文件名后缀
"""
def find_files_with_suffix(folder_path, suffix="_file"):
    found_files = []

    # os.walk()会生成一个元组（dirpath, dirnames, filenames）
    # 遍历目录树的每一个层次
    for dirpath, dirnames, filenames in os.walk(folder_path):
        # 遍历文件名是否以指定后缀结尾
        for filename in filenames:
            #检查文件名是否以指定后缀结尾
            if filename.endswith(suffix):
                # 如果符合条件，使用os.path.join()拼接完整路径并添加到列表
                file_path = os.path.join(dirpath, filename)
                found_files.append(file_path)
  
    return found_files

target_folder = "/Volumes/STORE/sex_files/tg"

files = find_files_with_suffix(target_folder, "_file")

if files:
    print(f"找到以下以'_file'结尾的文件：")
    for file in files:
        print(file)





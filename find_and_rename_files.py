import os

def find_and_rename_files(foloder_path, suffix="_file"):
    """
    遍历文件夹，找到文件名中包含特定后缀的文件，并重命名，
    在原有名称后添加 .mp4 扩展名。

    Args:
        folder_path (str): 要遍历的根目录路径。
        suffix (str): 要查找的文件名后缀。

    """
  
    # os.walk()遍历目录树
    for dirpath, dirnames, filenames in os.walk(foloder_path):
        for filename in filenames:
            # 检查文件名是否包含指定的后缀
            if suffix in filename:
                # 获取文件的完整原始路径
                original_path = os.path.join(dirpath, filename)

                # 构建新的文件名 
                new_filename = filename + ".mp4"

                # 构建新的完整路径
                new_path = os.path.join(dirpath, new_filename)

                try:
                    # 使用os.rename()重新命名文件
                    os.rename(original_path, new_path)
                    print(f"✅ 已重命名：\n - 原名：{original_path}\n - 新名：{new_path}")
                except OSError as e: 
                    print(f"❌ 错误：无法重命名文件 {original_path} - {e}")


# 路径
target_folder = "/Volumes/STORE/sex_files/tg"

find_and_rename_files(target_folder, "_file")

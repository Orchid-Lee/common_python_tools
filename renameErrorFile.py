import os

def fix_double_mp4_extension(root_dir):
    """
    递归查找目录及其子目录中所有以.mp4.mp4结尾的文件，并将其重命名为.mp4结尾
    """
    # 统计修复的文件数量
    fixed_count = 0
    
    # 递归遍历目录
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # 检查文件名是否以.mp4.mp4结尾且是文件（不是目录）
            if filename.endswith('.mp4.mp4'):
                # 构建完整路径
                old_path = os.path.join(dirpath, filename)
                
                # 确保是文件（不是目录）
                if not os.path.isfile(old_path):
                    continue
                
                # 生成新文件名（去掉最后一个.mp4）
                new_filename = filename[:-4]  # 从末尾移除4个字符（即".mp4"）
                new_path = os.path.join(dirpath, new_filename)
                
                # 检查新路径是否已存在
                if os.path.exists(new_path):
                    print(f"跳过：新路径已存在 - {new_path}")
                    continue
                
                # 执行重命名
                try:
                    os.rename(old_path, new_path)
                    print(f"已修复：{old_path} → {new_path}")
                    fixed_count += 1
                except Exception as e:
                    print(f"重命名失败 {old_path}：{str(e)}")
    
    print(f"\n处理完成，共修复 {fixed_count} 个文件")

def main():
    import sys
    # 检查是否提供了目录参数
    if len(sys.argv) != 2:
        print("使用方法：python fix_double_mp4.py <目标目录>")
        print("示例：python fix_double_mp4.py /Users/lee/Videos")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    # 检查目录是否存在
    if not os.path.isdir(target_dir):
        print(f"错误：目录不存在 - {target_dir}")
        sys.exit(1)
    
    # 开始修复
    print(f"开始处理目录：{target_dir}")
    fix_double_mp4_extension(target_dir)

if __name__ == "__main__":
    main()

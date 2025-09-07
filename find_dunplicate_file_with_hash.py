import os
import hashlib
import concurrent.futures
import multiprocessing

# --------------------------
# 在这里设置你要处理的目录路径
# 例如: TARGET_DIRECTORY = "/Users/yourname/Pictures"
# 或使用相对路径: TARGET_DIRECTORY = "./my_media_files"
TARGET_DIRECTORY = "/Users/lee/Downloads/telegram_download"
# --------------------------

# 媒体文件扩展名
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', 
                   '.heic', '.heif', '.psd', '.raw', '.cr2', '.nef')
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', 
                   '.mpg', '.m4v', '.qt', '.avchd', '.webm', '.mts')

def calculate_hash(file_path, block_size=65536):
    """计算文件前65536字节的SHA-256哈希值"""
    hasher = hashlib.sha256()
    try:
        if not os.access(file_path, os.R_OK):
            print(f"权限不足: {file_path}")
            return None
            
        with open(file_path, 'rb') as f:
            data = f.read(block_size)
            if data:
                hasher.update(data)
            return hasher.hexdigest()
    except Exception as e:
        print(f"处理错误 {file_path}: {str(e)}")
        return None

def is_media_file(file_path):
    """判断是否为媒体文件（排除macOS隐藏文件）"""
    if os.path.basename(file_path).startswith('.'):
        return False
        
    ext = os.path.splitext(file_path)[1].lower()
    return ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS

def process_file(file_path):
    """处理单个文件"""
    if is_media_file(file_path):
        file_hash = calculate_hash(file_path)
        if file_hash:
            return (file_path, file_hash)
    return None

def get_media_files(root_dir):
    """获取指定目录及其子目录中的所有媒体文件"""
    media_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        # 跳过macOS特殊目录和文件
        if '.DS_Store' in filenames:
            filenames.remove('.DS_Store')
        if any(exclude in dirpath for exclude in ('.git', '.svn', '.bundle')):
            continue
            
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if is_media_file(file_path):
                media_files.append(file_path)
    return media_files

def get_optimal_thread_count():
    """获取适合macOS的最佳线程数"""
    cpu_count = multiprocessing.cpu_count()
    return max(2, min(32, cpu_count * 2))  # 基于macOS I/O特性优化

def main():
    # 处理目录路径中的波浪号（macOS用户目录）
    root_dir = os.path.expanduser(TARGET_DIRECTORY)
    
    # 验证目录有效性
    if not os.path.isdir(root_dir):
        print(f"错误: 目录 '{root_dir}' 不存在或不是有效的目录")
        return

    print(f"正在扫描目录: {root_dir}")
    media_files = get_media_files(root_dir)
    print(f"发现 {len(media_files)} 个媒体文件，准备计算哈希值...")

    if not media_files:
        print("没有找到媒体文件")
        return

    # 使用优化的线程数
    max_workers = get_optimal_thread_count()
    print(f"使用 {max_workers} 个线程进行处理...")

    # 多线程处理
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, f): f for f in media_files}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                if len(results) % 10 == 0:
                    print(f"已完成 {len(results)}/{len(media_files)}")

    # 输出结果
    print("\n计算结果:")
    for file_path, file_hash in results:
        print(f"{file_hash}  {file_path}")

    print(f"\n完成！共处理 {len(results)} 个文件")

if __name__ == "__main__":
    main()
    
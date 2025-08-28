import os
import hashlib
from datetime import datetime
import mimetypes
import re

def has_chinese(text):
    """判断字符串是否包含中文"""
    if not text:
        return False
    # 匹配中文字符的正则表达式
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(pattern.search(text))

def get_file_hash(file_path, block_size=65536, max_blocks=100):
    """优化：仅读取文件前 max_blocks*block_size 字节计算哈希（默认约6.5MB）"""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            blocks_read = 0
            buf = f.read(block_size)
            while buf and blocks_read < max_blocks:
                hasher.update(buf)
                buf = f.read(block_size)
                blocks_read += 1
        return hasher.hexdigest()
    except Exception as e:
        print(f"计算文件 {file_path} 的哈希值时出错: {e}")
        return None

def get_file_mime_type(file_path):
    """获取文件的MIME类型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else 'unknown'

def is_media_file(file_path):
    """判断文件是否为图片或视频"""
    mime_type = get_file_mime_type(file_path)
    return mime_type.startswith(('image/', 'video/'))

def get_group_code_by_parent_folder(file_path):
    """根据文件的直接上层文件夹路径生成group_code"""
    try:
        parent_folder = os.path.dirname(file_path)
        folder_name = os.path.basename(parent_folder)
        
        # 对文件夹名称进行SHA-1哈希，支持中文
        hash_obj = hashlib.sha1(folder_name.encode('utf-8'))
        group_code = hash_obj.hexdigest()[:16]
        
        return group_code
    except Exception as e:
        print(f"生成group_code时出错: {e}")
        return 'unknown_folder'

def process_file(file_path):
    """处理单个文件的元数据提取，包含文件名特殊处理逻辑"""
    if not is_media_file(file_path):
        return None
    
    try:
        # 获取原始文件名和父路径
        original_filename = os.path.basename(file_path)
        parent_folder = os.path.dirname(file_path)
        parent_folder_name = os.path.basename(parent_folder)
        
        # 文件名处理逻辑：
        # 1. 检查原文件名是否包含中文
        filename_has_chinese = has_chinese(original_filename)
        
        # 2. 如果原文件名不含中文，检查父路径是否包含中文
        if not filename_has_chinese:
            parent_has_chinese = has_chinese(parent_folder)
            
            # 3. 若父路径包含中文，使用父路径名称作为文件名
            if parent_has_chinese:
                # 保留原文件扩展名
                file_ext = os.path.splitext(original_filename)[1]
                processed_filename = f"{parent_folder_name}{file_ext}"
            else:
                processed_filename = original_filename
        else:
            # 原文件名包含中文，直接使用
            processed_filename = original_filename
        
        # 获取其他文件属性
        stat_info = os.stat(file_path)
        file_size = stat_info.st_size
        
        # 时间处理
        created_time = datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
        if abs(modified_time.timestamp() - created_time.timestamp()) < 1:
            modified_time = None
        
        # 生成group_code
        group_code = get_group_code_by_parent_folder(file_path)
        
        # 其他元数据
        file_type = get_file_mime_type(file_path)
        hash_value = get_file_hash(file_path)
        
        return {
            'file_name': processed_filename,  # 使用处理后的文件名
            'file_path': file_path,
            'file_type': file_type,
            'file_size': file_size,
            'group_code': group_code,
            'hash_value': hash_value,
            'parent_folder': parent_folder,
            'created_time': created_time.isoformat(),
            'modified_time': modified_time.isoformat() if modified_time else None
        }
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def scan_media_files(root_dir):
    media_files = []
    file_paths = []
    
    # 收集所有媒体文件路径
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if is_media_file(file_path):
                file_paths.append(file_path)
    
    # 多线程处理
    import concurrent.futures
    max_workers = min(4, os.cpu_count())
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_file, file_paths)
        for result in results:
            if result:
                media_files.append(result)
                if len(media_files) % 100 == 0:
                    print(f"已处理 {len(media_files)} 个文件...")
    
    return media_files

def batch_insert_to_db(media_files, db_path):
    """批量插入数据库"""
    if not media_files:
        print("没有要插入的媒体文件数据")
        return
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT OR IGNORE INTO media_metadata 
        (file_name, file_path, file_type, file_size, group_code, 
         hash_value, parent_folder, created_time, modified_time)
        VALUES (:file_name, :file_path, :file_type, :file_size, :group_code,
                :hash_value, :parent_folder, :created_time, :modified_time)
        """
        
        cursor.executemany(insert_sql, media_files)
        conn.commit()
        print(f"成功插入 {cursor.rowcount} 条记录到数据库")
        
    except sqlite3.Error as e:
        print(f"数据库操作出错: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def main():
    # 配置参数：根目录 /Volumes/STORE/sex_files/tg    /Volumes/STORE/sex_files/telegram_download
    # 替换为你的实际根目录
    root_directory = "/Volumes/STORE/sex_files/tg"  
    db_path = "/Users/lee/sqlite3/media_player.db"
    
    print(f"开始扫描目录: {root_directory}")
    media_files = scan_media_files(root_directory)
    
    print(f"扫描完成，共发现 {len(media_files)} 个媒体文件")
    if media_files:
        batch_insert_to_db(media_files, db_path)
    
    print("操作完成")

if __name__ == "__main__":
    main()

import sqlite3
import os
import ffmpeg
import sys

# 数据库和文件目录配置
DATABASE_PATH = '/Users/lee/sqlite3/media_player.db'
# 请确保这个路径与你的Flask应用中配置的TARGET_FOLDER一致
TARGET_FOLDER = "/Volumes/STORE/sex_files/telegram_download" 

# --- 1. 视频封面生成函数 ---
def generate_video_poster(video_path: str, output_poster_path: str, timestamp: str = '00:00:05') -> bool:
    """
    使用 ffmpeg 从视频中提取指定时间点的一帧作为海报。
    
    :param video_path: 视频文件的完整路径
    :param output_poster_path: 生成的海报图片的完整路径
    :param timestamp: 提取帧的时间点，默认为'00:00:05'（第5秒）
    :return: 成功返回True，失败返回False
    """
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在于 {video_path}")
        return False
    
    try:
        # 使用 ffmpeg-python 提取帧，并指定输出路径
        (
            ffmpeg
            .input(video_path, ss=timestamp) # 从指定时间点开始
            .output(output_poster_path, vframes=1) # 只输出一帧
            .run(overwrite_output=True, capture_stderr=True)
        )
        print(f"成功为 {os.path.basename(video_path)} 生成海报: {output_poster_path}")
        return True
        
    except ffmpeg.Error as e:
        print(f"为 {os.path.basename(video_path)} 生成海报失败:")
        print(e.stderr.decode('utf8'))
        return False
    except Exception as e:
        print(f"发生意外错误: {e}")
        return False

# --- 2. 数据库操作主函数 ---
def main():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询所有类型为视频且poster_path为空的记录
        cursor.execute("""
            SELECT file_path, parent_folder, group_code 
            FROM media_data 
            WHERE file_type LIKE 'video/%' AND (poster_path IS NULL OR poster_path = '')
        """)
        
        rows = cursor.fetchall()
        print(f"找到 {len(rows)} 个待生成封面的视频文件...")
        
        for row in rows:
            video_path = row['file_path']
            parent_folder = row['parent_folder']
            group_code = row['group_code']
            
            # 构造海报文件路径，名称格式为poster_{group_code}.jpeg
            # 确保父文件夹存在
            if not os.path.exists(parent_folder):
                print(f"警告: 父文件夹不存在，跳过: {parent_folder}")
                continue

            poster_name = f"poster_{group_code}.jpeg"
            poster_path = os.path.join(parent_folder, poster_name)
            
            # 调用封面生成函数
            if generate_video_poster(video_path, poster_path):
                # 如果封面生成成功，则更新数据库
                try:
                    update_cursor = conn.cursor()
                    update_cursor.execute("""
                        UPDATE media_data
                        SET poster_path = ?
                        WHERE file_path = ?
                    """, (poster_path, video_path))
                    conn.commit()
                    print(f"数据库记录已更新: {os.path.basename(video_path)}")
                except sqlite3.Error as e:
                    print(f"更新数据库失败: {e}")
                    conn.rollback()
            else:
                print(f"跳过更新数据库，因为海报生成失败: {os.path.basename(video_path)}")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("脚本执行完毕，数据库连接已关闭。")

if __name__ == "__main__":
    main()
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sqlite3
import os
import mimetypes
from functools import wraps, lru_cache
from datetime import datetime, timedelta, timezone  # 新增timezone导入

app = Flask(__name__)
CORS(app)

# 'TARGET_FOLDER': "/Volumes/STORE/sex_files/telegram_download"
# 配置项 - 集中管理配置
app.config.update({
    'DATABASE_PATH': '/Users/lee/sqlite3/media_player.db',  # 数据库文件路径
    'TARGET_FOLDER': "/Volumes/STORE/",  # 基础文件目录
    'DEFAULT_PAGE_SIZE': 800,  # 默认每页记录数
    'MAX_PAGE_SIZE': 800,     # 最大每页记录数
    'CACHE_TIMEOUT': 300      # 缓存超时时间(秒)
})

# 数据库连接工具函数
def get_db_connection():
    """创建数据库连接并返回连接和游标"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row  # 使查询结果可通过列名访问
    return conn, conn.cursor()

def close_db_connection(conn):
    """关闭数据库连接"""
    if conn:
        try:
            conn.close()
        except Exception as e:
            app.logger.error(f"关闭数据库连接失败: {str(e)}")

# 缓存装饰器 - 带超时功能
def timed_lru_cache(seconds: int, maxsize: int = 128):
    """带超时的LRU缓存装饰器"""
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.now(timezone.utc) + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.now(timezone.utc) >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.now(timezone.utc) + func.lifetime
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper_cache

# 数据库查询函数 - 带分页支持
def get_files_from_db(
    file_type=None, 
    group_code=None, 
    page=1, 
    page_size=app.config['DEFAULT_PAGE_SIZE']
):
    """
    从数据库查询文件信息（支持分页）
    :param file_type: 可选，筛选类型('video'或'image')
    :param group_code: 可选，按group_code筛选
    :param page: 页码，从1开始
    :param page_size: 每页记录数
    :return: 分页文件数据和总记录数
    """
    # 验证分页参数
    if page < 1:
        page = 1
    if page_size < 1 or page_size > app.config['MAX_PAGE_SIZE']:
        page_size = app.config['DEFAULT_PAGE_SIZE']
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    conn, cursor = None, None
    try:
        conn, cursor = get_db_connection()
        
        # 基础查询SQL和计数SQL
        base_query = """
        SELECT file_name, file_path, file_type, group_code, parent_folder, 
               file_size, created_time, modified_time, poster_path 
        FROM media_data 
        WHERE 1=1
        """
        count_query = "SELECT COUNT(*) as total FROM media_data WHERE 1=1"
        params = []
        
        # 添加类型筛选条件
        if file_type == 'video':
            base_query += " AND file_type LIKE 'video/%'"
            count_query += " AND file_type LIKE 'video/%'"
        elif file_type == 'image':
            base_query += " AND file_type LIKE 'image/%'"
            count_query += " AND file_type LIKE 'image/%'"
        
        # 添加分组筛选条件
        if group_code:
            base_query += " AND group_code = ?"
            count_query += " AND group_code = ?"
            params.append(group_code)
        
        # 执行计数查询
        cursor.execute(count_query, params.copy())
        total = cursor.fetchone()['total']
        
        # 添加排序和分页
        base_query += " ORDER BY parent_folder, created_time DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        # 执行数据查询
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        print(f"数据库数据：{rows[0]['poster_path']}")
        # 整理数据
        files_data = []
        for row in rows:
            file_ext = os.path.splitext(row['file_name'])[1].lower()
            files_data.append({
                'name': row['file_name'],
                'path': row['file_path'],
                'type': 'video' if row['file_type'].startswith('video/') else 'image',
                'ext': file_ext,
                'size': row['file_size'],
                'created_time': row['created_time'],
                'modified_time': row['modified_time'],
                'group_code': row['group_code'],
                'parent_folder': row['parent_folder'],
                'poster_path': row['poster_path']
            })
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return {
            'data': files_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        }
        
    except sqlite3.Error as e:
        app.logger.error(f"数据库查询错误: {str(e)}")
        return {
            'data': [],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': 0,
                'total_pages': 0
            }
        }
    finally:
        close_db_connection(conn)

# 按文件夹分组的查询（用于需要按文件夹浏览的场景）
@timed_lru_cache(seconds=app.config['CACHE_TIMEOUT'])
def get_files_by_folder_from_db(file_type=None, group_code=None):
    """按文件夹分组查询文件（不带分页，用于文件夹列表展示）"""
    conn, cursor = None, None
    try:
        conn, cursor = get_db_connection()
        
        query = """
        SELECT file_name, file_path, file_type, group_code, parent_folder, 
               file_size, created_time, modified_time, poster_path
        FROM media_data 
        WHERE 1=1
        """
        params = []
        
        if file_type == 'video':
            query += " AND file_type LIKE 'video/%'"
        elif file_type == 'image':
            query += " AND file_type LIKE 'image/%'"
        
        if group_code:
            query += " AND group_code = ?"
            params.append(group_code)
            
        query += " ORDER BY parent_folder, created_time DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 按文件夹分组
        folders_data = {}
        for row in rows:
            folder = row['parent_folder']
            if folder not in folders_data:
                folders_data[folder] = {
                    'folder': folder,
                    'file_count': 0,
                    'files': []
                }
            
            file_ext = os.path.splitext(row['file_name'])[1].lower()
            folders_data[folder]['files'].append({
                'name': row['file_name'],
                'path': row['file_path'],
                'type': 'video' if row['file_type'].startswith('video/') else 'image',
                'ext': file_ext,
                'size': row['file_size'],
            })

            if row['file_type'].startswith('video/'):
                folders_data[folder]['poster_path'] = row['poster_path']
            else:
                folders_data[folder]['poster_path'] = row['file_path']
                
            folders_data[folder]['poster_path'] = row['file_path']
            folders_data[folder]['file_count'] += 1
        
        return list(folders_data.values())
        
    except sqlite3.Error as e:
        app.logger.error(f"按文件夹查询错误: {str(e)}")
        return []
    finally:
        close_db_connection(conn)

# API接口
@app.route("/api/files", methods=["GET"])
def get_files():
    """
    获取文件列表（支持分页）
    支持参数:
    - type: 可选，筛选类型('video'或'image')
    - group_code: 可选，按group_code筛选
    - page: 可选，页码(默认1)
    - page_size: 可选，每页记录数(默认50，最大200)
    """
    # 解析请求参数
    file_type = request.args.get('type')
    group_code = request.args.get('group_code')
    
    # 解析分页参数
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', app.config['DEFAULT_PAGE_SIZE']))
    except ValueError:
        return jsonify({"error": "页码和每页记录数必须是整数"}), 400
    
    # 验证类型参数
    if file_type and file_type not in ['video', 'image']:
        return jsonify({"error": "无效的类型参数，可选值为'video'或'image'"}), 400
    
    # 查询数据
    result = get_files_from_db(
        file_type=file_type,
        group_code=group_code,
        page=page,
        page_size=page_size
    )
    
    return jsonify(result)

@app.route("/api/folders", methods=["GET"])
def get_folders():
    """
    获取文件夹列表（包含每个文件夹的文件摘要）
    支持参数:
    - type: 可选，筛选类型('video'或'image')
    - group_code: 可选，按group_code筛选
    """
    file_type = request.args.get('type')
    group_code = request.args.get('group_code')
    
    if file_type and file_type not in ['video', 'image']:
        return jsonify({"error": "无效的类型参数，可选值为'video'或'image'"}), 400
    
    folders_data = get_files_by_folder_from_db(file_type, group_code)
    return jsonify({
        'total_folders': len(folders_data),
        'total_files': sum(folder['file_count'] for folder in folders_data),
        'data': folders_data
    })

@app.route("/api/stream", methods=["GET"])
def stream_file():
    """流式传输文件"""
    file_path = request.args.get('path')
    
    # 验证参数
    if not file_path:
        return jsonify({"error": "缺少文件路径参数"}), 400
    
    # 安全检查：确保文件在允许的目录内
    allowed_root = os.path.abspath(app.config['TARGET_FOLDER'])
    file_abspath = os.path.abspath(file_path)
    
    # 严格验证路径，防止路径遍历攻击
    if os.path.commonprefix([file_abspath, allowed_root]) != allowed_root:
        app.logger.warning(f"尝试访问未授权路径: {file_path}")
        return jsonify({"error": "访问被拒绝"}), 403
    
    # 验证文件是否存在
    if not os.path.isfile(file_abspath):
        return jsonify({"error": "文件不存在"}), 404
    
    # 获取MIME类型
    mime_type, _ = mimetypes.guess_type(file_abspath)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    # 大文件流式传输
    def generate():
        with open(file_abspath, 'rb') as f:
            while chunk := f.read(1024 * 1024):  # 1MB块
                yield chunk
    
    return Response(generate(), mimetype=mime_type)

@app.route("/api/refresh-cache", methods=["POST"])
def refresh_cache():
    """刷新缓存接口"""
    get_files_by_folder_from_db.cache_clear()
    return jsonify({"message": "缓存已刷新"})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "资源不存在"}), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"服务器内部错误: {str(error)}")
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)

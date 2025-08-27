from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from find_duplicate_files import find_duplicate_files
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

# 定义支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    'videos': ['.mp4', '.avi', '.mov', '.mkv', '.flv'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
}

TARGET_FOLDER = "/Volumes/STORE/sex_files/telegram_download"

def scan_files(root_folder):
    """
    扫描指定文件夹以及子文件夹，获取支持的视频和图片文件
    """

    if not os.path.isdir(root_folder):
        return {}
    
    # 使用 defaultdict(list)自动创建键值和列表
    folders_data = defaultdict(list)
     
    for root, _, files in os.walk(root_folder):
        for filename in files:
            # 获取文件的扩展名，并转换为小写
            file_ext = os.path.splitext(filename)[1].lower()

            file_type = None
            if file_ext in SUPPORTED_EXTENSIONS['videos']:
                file_type = 'video'
            elif file_ext in SUPPORTED_EXTENSIONS['images']:
                file_type = 'image'
            
            if file_type:
                folders_data[root].append({
                    "name": filename,
                    "path": os.path.join(root, filename),
                    "type": file_type
                })

    return folders_data

@app.route("/api/files", methods=["GET"])
def get_files():
    """
    API接口：返回所有视频和图文列表
    """
    # 扫描文件，获取数据
    files_data = scan_files(TARGET_FOLDER)

    # 数据转化为列表格式
    formatted_data = []
    for folder_path, files, in files_data.items():
        formatted_data.append({
            "folder": folder_path,
            "files": files
        })
    # 将数据以JSON格式返回给前端
    return jsonify(formatted_data)

# 新增的流媒体接口
@app.route('/api/stream')
def stream_file():
    # 从请求参数中获取文件路径
    file_path = request.args.get('path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found."}), 404

    # 确保请求的路径在允许的根目录下，以防范路径遍历攻击
    if not file_path.startswith(os.path.abspath(TARGET_FOLDER)):
        return jsonify({"error": "Access denied."}), 403

    return send_file(file_path)

if __name__ == '__main__':
    #  启动Flask应用
    app.run(debug=True)
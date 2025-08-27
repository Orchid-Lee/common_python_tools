import os 
def generate_video_list_html(folder_path, output_filename="video_list.html"):
    """
    遍历指定文件夹及其子文件夹，找到所有视频文件，并生成一个HTML网页。

    Args:
        folder_path (str): 要遍历的根目录路径。
        output_filename (str): 生成的HTML文件名称。
    """
    # 定义长间的视频文件扩展名
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.ts', '.wmv']

    found_videos = []
    print("正在搜索视频文件...")

    # 遍历目录树，找到所有视频文件
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                # 确保路径格式正确
                full_path = os.path.join(dirpath, filename)
                # 将路径转换为URL格式，使用file://协议，并处理空格等特殊字符
                url_path = "file://" + full_path.replace(os.sep, "/")
                found_videos.append(url_path)
    
    # 生成HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>视频文件列表</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; margin: 2em; background-color: #f4f4f4; color: #333; }}
            h1 {{ color: #005A9C; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin-bottom: 0.5em; }}
            a {{ color: #007BFF; text-decoration: none; word-wrap: break-word; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>视频文件列表</h1>
        <p>点击以下链接将使用系统默认播放器打开视频。如果您想用 IINA 打开，请确保您的macOS系统已配置了 `iina://` URI 协议。</p>
        <ul>
    """

    if found_videos:
        for video_path in found_videos:
            display_name = os.path.basename(video_path.replace("file://", ""))
            # 注意：这里使用os.path.basename 提取文件名作为显示名称
            html_content += f'            <li><a href="{video_path}">{display_name}</a></li>\n'
    else:
        html_content += '            <li>未找到任何视频文件。</li>\n'

    html_content += """
        </ul>
    </body>
    </html>
    """

    # 将html内容写入文件
    try: 
        with open(output_filename, "w", encoding= "utf-8") as f:
            f.write(html_content)
        print(f"✅ HTML 网页已成功生成：{os.path.abspath(output_filename)}")
        print(f"请在浏览器中打开此文件。")
    except Exception as e:
        print(f"❌ 无法写入文件：{e}")

# ---------- 示例用法 ----------
# 替换成你要遍历的文件夹路径，例如：
# /Users/your_name/Videos
# /Volumes/External_HDD/My_Movies
target_folder_path = "/Volumes/STORE/sex_files/tg" 

home_directory = os.path.expanduser("~")
desktop_path = os.path.join(home_directory, "Desktop")
output_html_path = os.path.join(desktop_path, "video_list.html")

generate_video_list_html(target_folder_path, output_html_path)

import os 

path = '/Users/lee/Downloads/telegram_download'

for root, dirs, files in os.walk(path):
    print(f"Current directory: {root}")
    print(f"Subdirectories: {dirs}")
    print(f"Files: {files}")
    print("-" * 20)

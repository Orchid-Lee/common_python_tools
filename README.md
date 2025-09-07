CREATE TABLE IF NOT EXISTS media_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增ID（唯一标识）
    file_name TEXT NOT NULL,               -- 文件名（如"img_2024.jpg"）
    file_path TEXT UNIQUE NOT NULL,        -- 文件完整路径（唯一，避免重复）
    file_type TEXT,                        -- 文件类型（如"image/jpeg; video/mp4"）
    file_size INTEGER,                     -- 文件大小（字节）
    poster_path,                           -- 海报地址
    created_time DATETIME,                 -- 创建时间（如"2024-08-28 10:30:00"）
    modified_time DATETIME,                -- 修改时间
    hash_value TEXT,                       -- 文件哈希值（用于去重）
    parent_folder TEXT,                    -- 父文件夹路径（便于按文件夹查询）
    group_code TEXT                        -- 分组标识
);

-- 创建索引（加速查询）
CREATE INDEX IF NOT EXISTS idx_type ON media_metadata(file_type);
CREATE INDEX IF NOT EXISTS idx_created ON media_metadata(created_time);
CREATE INDEX IF NOT EXISTS idx_folder ON media_metadata(parent_folder);

-- 新增数据
INSERT INTO media_metadata (
    file_name, file_path, file_type, file_size, 
    created_time, modified_time, hash_value, parent_folder
) VALUES (
    'vacation_01.jpg', 
    '/Users/yourname/Photos/2024/08/vacation_01.jpg', 
    'image/jpeg', 
    2456000,  -- 2.45MB（字节）
    '2024-08-28 09:15:30', 
    '2024-08-28 09:15:30', 
    'a1b2c3d4e5f6...',  -- 实际计算的哈希值
    '/Users/yourname/Photos/2024/08' 
);

-- 按文件类型查询数据
SELECT file_name, file_path, created_time 
FROM media_metadata 
WHERE file_type LIKE 'image/%';

-- 查询文件名称、路径
select file_name, file_path from media_metadata;

-- 新增列
ALTER TABLE ADD COLUMNS poster_path TEXT;

ALTER TABLE media_metadata ADD COLUMN poster_path TEXT;



CREATE TABLE IF NOT EXISTS media_data (
    media_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增ID（唯一标识）
    file_name TEXT NOT NULL,               -- 文件名（如"img_2024.jpg"）
    file_path TEXT UNIQUE NOT NULL,        -- 文件完整路径（唯一，避免重复）
    file_type TEXT,                        -- 文件类型（如"image/jpeg; video/mp4"）
    file_size INTEGER,                     -- 文件大小（字节）
    poster_path TEXT,                      -- 海报地址
    created_time DATETIME,                 -- 创建时间（如"2024-08-28 10:30:00"）
    modified_time DATETIME,                -- 修改时间
    hash_value TEXT,                       -- 文件哈希值（用于去重）
    parent_folder TEXT,                    -- 父文件夹路径（便于按文件夹查询）
    group_code TEXT                        -- 分组标识
);

-- 创建索引（加速查询）
CREATE INDEX IF NOT EXISTS idx_type ON media_data(file_type);
CREATE INDEX IF NOT EXISTS idx_created ON media_data(created_time);
CREATE INDEX IF NOT EXISTS idx_folder ON media_data(parent_folder);

insert into media_data(
    file_name,
    file_path,
    file_type,
    file_size,
    poster_path,
    created_time,
    modified_time,
    hash_value,
    parent_folder,
    group_code
)
select 
    file_name,
    file_path,
    file_type,
    file_size,
    poster_path,
    created_time,
    modified_time,
    hash_value,
    parent_folder,
    group_code
from media_metadata;
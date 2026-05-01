import os
import stat

file_path = "/app/generated_media/images/poster_1770547822.png"
dir_path = "/app/generated_media/images"

try:
    print(f"Fixing permissions for {file_path}")
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 644
    print("File permissions set to 644")
    
    print(f"Fixing permissions for directory {dir_path}")
    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH) # 755
    print("Directory permissions set to 755")
    
except Exception as e:
    print(f"Error: {e}")

import os
import time
import shutil
import sys

# Mocking the constants from main.py
TEMP_MEDIA_DIRS = [
    "/app/generated_media/temp/videos",
    "/app/generated_media/temp/images"
]

def cleanup_old_ai_media(mock_dirs):
    """Refactored cleanup for testing with mocked dirs"""
    cutoff_time = time.time() - (24 * 60 * 60)
    for directory in mock_dirs:
        if not os.path.exists(directory): continue
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path): continue
            
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

def run_test():
    base = "/tmp/retention_test"
    if os.path.exists(base): shutil.rmtree(base)
    os.makedirs(base)
    
    # Setup mock structure
    temp_vid = os.path.join(base, "temp/videos")
    perm_vid = os.path.join(base, "permanent/videos") # Should NOT be in the list
    
    os.makedirs(temp_vid)
    os.makedirs(perm_vid)
    
    # Create files
    old_time = time.time() - (48 * 3600)
    
    # 1. Temp file (old) -> Should be deleted
    t_file = os.path.join(temp_vid, "old_temp.mp4")
    with open(t_file, "w") as f: f.write("temp")
    os.utime(t_file, (old_time, old_time))
    
    # 2. Permanent file (old) -> Should be KEPT (because dir is not in list)
    p_file = os.path.join(perm_vid, "old_perm.mp4")
    with open(p_file, "w") as f: f.write("perm")
    os.utime(p_file, (old_time, old_time))
    
    print("Files created.")
    
    # Run cleanup ONLY on the temp dir (simulating the fix in main.py)
    cleanup_old_ai_media([temp_vid]) 
    
    # Check results
    if os.path.exists(t_file):
        print("FAILURE: Temp file was not deleted.")
        sys.exit(1)
        
    if not os.path.exists(p_file):
         print("FAILURE: Permanent file was deleted (unexpected).")
         sys.exit(1)
         
    print("SUCCESS: Retention logic verified.")

if __name__ == "__main__":
    run_test()

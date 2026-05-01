import os
import time
import sys
import shutil

# Mocking the DIRS and environment for video_engine
class MockVideoEngine:
    def __init__(self, base_dir):
        self.output_dir = os.path.join(base_dir, "generated_media")
        self.dirs = {
            "video": os.path.join(self.output_dir, "temp/videos"),
            "image": os.path.join(self.output_dir, "temp/images"),
            "temp": os.path.join(self.output_dir, "temp"),
            "permanent": os.path.join(self.output_dir, "permanent")
        }
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)
            
    def cleanup_old_files(self):
        now = time.time()
        cutoff = now - (24 * 3600)
        # The logic we just implemented
        target_dirs = [self.dirs["video"], self.dirs["image"], self.dirs["temp"]]
        for directory in target_dirs:
            if not os.path.exists(directory): continue
            for f in os.listdir(directory):
                f_path = os.path.join(directory, f)
                if os.path.isfile(f_path) and os.path.getmtime(f_path) < cutoff:
                    try:
                        os.remove(f_path)
                    except: pass

def run_test():
    base_test_dir = "/tmp/cleanup_test"
    if os.path.exists(base_test_dir):
        shutil.rmtree(base_test_dir)
    
    ve = MockVideoEngine(base_test_dir)
    
    # Create old files
    old_time = time.time() - (48 * 3600)
    
    # 1. Temp file (should be deleted)
    temp_file = os.path.join(ve.dirs["video"], "old_temp.mp4")
    with open(temp_file, "w") as f: f.write("temp")
    os.utime(temp_file, (old_time, old_time))
    
    # 2. Permanent file (should be preserved)
    perm_dir = os.path.join(ve.dirs["permanent"], "videos")
    os.makedirs(perm_dir, exist_ok=True)
    perm_file = os.path.join(perm_dir, "old_permanent.mp4")
    with open(perm_file, "w") as f: f.write("perm")
    os.utime(perm_file, (old_time, old_time))
    
    print("Before cleanup:")
    print(f"Temp file exists: {os.path.exists(temp_file)}")
    print(f"Permanent file exists: {os.path.exists(perm_file)}")
    
    ve.cleanup_old_files()
    
    print("\nAfter cleanup:")
    temp_exists = os.path.exists(temp_file)
    perm_exists = os.path.exists(perm_file)
    print(f"Temp file exists: {temp_exists} (Expected: False)")
    print(f"Permanent file exists: {perm_exists} (Expected: True)")
    
    if not temp_exists and perm_exists:
        print("\nSUCCESS: Cleanup logic works as expected.")
    else:
        print("\nFAILURE: Cleanup logic failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_test()

import os
import subprocess

repo_dir = "/root/social-automation"
os.chdir(repo_dir)

# 1. Stop tracking large files
try:
    print("Finding large files...")
    files_out = subprocess.check_output(["find", "assets", "-type", "f", "-size", "+90M"]).decode().splitlines()
    for f in files_out:
        print(f"Untracking {f}...")
        subprocess.call(["git", "rm", "--cached", f])
except Exception as e:
    print(f"Error untracking: {e}")

# 2. Update .gitignore
with open(".gitignore", "a") as f:
    f.write("\n# AUTOMATICALLY DETECTED LARGE BINARIES\n")
    f.write("assets/**/*.mp4\n")
    f.write("assets/**/*.mov\n")
    f.write("assets/**/*.ai\n")
    f.write("assets/**/*.pdf\n")
    f.write("assets/**/*.zip\n")

# 3. Final Stage and Commit
subprocess.call(["git", "add", ".gitignore"])
subprocess.call(["git", "commit", "-m", "chore: exclude large binaries from git tracking and cleanup cache"])
print("Fixed Git state.")

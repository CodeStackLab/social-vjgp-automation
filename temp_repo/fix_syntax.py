import os

filepath = "/root/social-automation/app/templates/index.html"
with open(filepath, "r") as f:
    lines = f.readlines()

new_lines = []
skip_next_else = False
for line in lines:
    if 'else { try { const resp = JSON.parse(xhr.responseText);' in line:
        new_lines.append(line)
        skip_next_else = True
        continue
    
    if skip_next_else and 'else reject(xhr.statusText);' in line:
        # This is the redundant one, skip it
        skip_next_else = False
        continue
    
    new_lines.append(line)

with open(filepath, "w") as f:
    f.writelines(new_lines)
print("Successfully fixed syntax error in index.html")

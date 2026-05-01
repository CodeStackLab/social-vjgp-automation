import os

filepath = "/root/social-automation/app/templates/index.html"
with open(filepath, "r") as f:
    lines = f.readlines()

# We want to find the uploadAsset function and inject better error reporting
# Search for: if (xhr.status >= 200 && xhr.status < 300) resolve();
# Replace with: 
# if (xhr.status >= 200 && xhr.status < 300) resolve();
# else {
#     try {
#         const resp = JSON.parse(xhr.responseText);
#         reject(resp.message || xhr.statusText);
#     } catch(e) { reject(xhr.statusText); }
# }

for i, line in enumerate(lines):
    if "if (xhr.status >= 200 && xhr.status < 300) resolve();" in line:
        lines[i] = "                        if (xhr.status >= 200 && xhr.status < 300) resolve();\n"
        lines.insert(i+1, "                        else { try { const resp = JSON.parse(xhr.responseText); reject(resp.message || xhr.statusText); } catch(e) { reject(xhr.statusText); } }\n")
        break

# Also update the alert in the .catch block
for i, line in enumerate(lines):
    if 'alert("Upload failed for " + file.name);' in line:
        lines[i] = '                    alert("Upload failed for " + file.name + ": " + err);\n'
        break

with open(filepath, "w") as f:
    f.writelines(lines)
print("Successfully patched index.html")

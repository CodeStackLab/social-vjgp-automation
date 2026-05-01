import os

filepath = "/root/social-automation/app/main.py"
with open(filepath, "r") as f:
    lines = f.readlines()

new_func = [
    "@app.route('/api/assets/upload', methods=['POST'])\n",
    "@login_required\n",
    "def upload_asset():\n",
    "    try:\n",
    "        file = request.files.get('file')\n",
    "        if not file:\n",
    "            return jsonify({\"status\": \"error\", \"message\": \"No file provided\"}), 400\n",
    "\n",
    "        filename = secure_filename(file.filename)\n",
    "        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''\n",
    "        \n",
    "        if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:\n",
    "            category = 'logos' if 'logo' in filename.lower() else 'images'\n",
    "        elif ext == 'pdf':\n",
    "            category = 'pdfs'\n",
    "        elif ext in ['mp4', 'mov', 'avi', 'webm', 'mkv', 'flv']:\n",
    "            category = 'videos'\n",
    "        else:\n",
    "            category = 'images'  # default\n",
    "        \n",
    "        save_dir = f'/app/generated_media/permanent/{category}'\n",
    "        os.makedirs(save_dir, exist_ok=True)\n",
    "        \n",
    "        save_path = os.path.join(save_dir, filename)\n",
    "        file.save(save_path)\n",
    "        \n",
    "        # Ensure world-readable for serving\n",
    "        os.chmod(save_path, 0o644)\n",
    "        \n",
    "        add_log(\"Upload\", \"INFO\", f\"Uploaded {filename} to {category}\")\n",
    "        return jsonify({\"status\": \"success\", \"path\": f\"permanent/{category}/{filename}\"})\n",
    "    except Exception as e:\n",
    "        import traceback\n",
    "        error_trace = traceback.format_exc()\n",
    "        add_log(\"Upload\", \"ERROR\", f\"Failed to upload: {str(e)}\")\n",
    "        print(error_trace)\n",
    "        return jsonify({\"status\": \"error\", \"message\": str(e)}), 500\n"
]

# Find the start of the old function
start_idx = -1
for i, line in enumerate(lines):
    if "@app.route('/api/assets/upload'" in line:
        start_idx = i
        break

if start_idx != -1:
    # Find the end of the function (where the next route or function starts)
    end_idx = start_idx + 1
    while end_idx < len(lines) and not lines[end_idx].startswith("@app.route") and not lines[end_idx].startswith("def"):
        end_idx += 1
    
    # Replace
    lines[start_idx:end_idx] = new_func

    with open(filepath, "w") as f:
        f.writelines(lines)
    print("Successfully patched main.py")
else:
    print("Could not find upload_asset route")

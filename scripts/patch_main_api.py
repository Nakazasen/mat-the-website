import sys
import os

# Try to find main.py relative to the script or current directory
possible_paths = [
    "main.py",
    "backend/main.py",
    "../backend/main.py",
    "c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/main.py"
]

file_path = None
for p in possible_paths:
    if os.path.exists(p):
        file_path = p
        break

if not file_path:
    print("ERROR: Could not find main.py")
    sys.exit(1)

print(f"DEBUG: Patching {file_path}")

try:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
except Exception as e:
    print(f"ERROR: Could not read file: {e}")
    sys.exit(1)

# 1. Update NovelSettings class
found_class = False
for i, line in enumerate(lines):
    if "class NovelSettings(BaseModel):" in line:
        print(f"DEBUG: Found class NovelSettings at line {i+1}")
        for j in range(i+1, i+20):
            if "total_likes: int = 0" in lines[j]:
                print(f"DEBUG: Adding ai_model_name field after line {j+1}")
                lines[j] = lines[j] + '    ai_model_name: str = "gemini-1.5-flash"\n\n\nclass AdminNovelUpdate(BaseModel):\n    title: Optional[str] = None\n    author: Optional[str] = None\n    description: Optional[str] = None\n    status: Optional[str] = None\n    genres: Optional[list[str]] = None\n    ai_model_name: Optional[str] = None\n'
                found_class = True
                break
    if found_class: break

# 2. Update get_novel_settings logic
found_logic1 = False
for i, line in enumerate(lines):
    if 'final_data["total_likes"] = total_likes' in line:
        print(f"DEBUG: Found logic mapping at line {i+1}")
        lines[i] = '        final_data["total_likes"] = total_likes\n        final_data["ai_model_name"] = resp.data.get("ai_model_name", "gemini-1.5-flash")\n'
        found_logic1 = True
        break

# 3. Update fallback logic and add PUT route
found_fallback = False
for i, line in enumerate(lines):
    if "total_likes=0" in line and i > 500:
        print(f"DEBUG: Found fallback at line {i+1}")
        lines[i] = '            total_likes=0,\n            ai_model_name="gemini-1.5-flash"\n'
        for j in range(i+1, i+10):
            if "        )" in lines[j]:
                print(f"DEBUG: Adding Admin PUT route after line {j+1}")
                lines[j] = lines[j] + '\n\n@app.put("/api/admin/novel", summary="[Admin] Cập nhật thông tin truyện & cấu hình hệ thống")\nasync def admin_update_novel(\n    body: AdminNovelUpdate,\n    authorization: Optional[str] = Header(None),\n):\n    """Cập nhật các thông tin chung của truyện và cấu hình AI."""\n    await verify_admin(authorization)\n    \n    data = body.model_dump(exclude_none=True)\n    if not data:\n        return {"message": "Không có gì thay đổi"}\n    \n    # Update novel settings (ID 1)\n    result = supabase.table("novel_settings").upsert({**data, "id": 1}).execute()\n    return {"message": "Cập nhật thành công", "data": result.data[0]}\n'
                found_fallback = True
                break
    if found_fallback: break

if found_class and found_logic1 and found_fallback:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("SUCCESS: backend/main.py updated.")
    except Exception as e:
        print(f"ERROR: Could not write file: {e}")
        sys.exit(1)
else:
    print(f"FAILED: found_class={found_class}, found_logic1={found_logic1}, found_fallback={found_fallback}")
    # Print a few lines for debug
    sys.exit(1)

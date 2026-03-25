import os

file_path = "backend/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

def print_context(target_line_num):
    # target_line_num is 1-based
    idx = target_line_num - 1
    start = max(0, idx - 5)
    end = min(len(lines), idx + 5)
    print(f"--- Context around line {target_line_num} ---")
    for i in range(start, end):
        print(f"{i+1}: {repr(lines[i])}")

print_context(471)
print_context(513)
print_context(529)

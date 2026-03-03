import re

path = "/Users/yu/Desktop/seigei/server/app.py"
with open(path) as f:
    content = f.read()

# Replace the broken block with clean code
old_block = '''        # Strip model-generated session state headers and metadata
        clean = _re.sub(r"#+ ?Session State.*?(?=\n[A-Z]|\n[a-z]|\n"|\n\')", "", clean, flags=_re.DOTALL)
        clean = _re.sub(r"#+ ?Segment \\d+\\s*", "", clean)
        clean = _re.sub(r"Phase:.*?(?:Segment|Intensity):.*?\n", "", clean)
        clean = _re.sub(r"---+", "", clean)'''

# Since the broken text has literal newlines, find it by unique markers
start_marker = "# Strip model-generated session state"
end_marker = 'clean = clean.replace("\\n"'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx > 0 and end_idx > start_idx:
    # Find the start of the line containing start_marker
    line_start = content.rfind("\n", 0, start_idx) + 1
    
    replacement = '''        # Strip model-generated session state headers and metadata
        clean = _re.sub(r"#+\\s*Session State[^a-z]*?(?=[A-Z][a-z])", "", clean)
        clean = _re.sub(r"#+\\s*Segment \\d+\\s*", "", clean)
        clean = _re.sub(r"Phase:.*?Intensity:.*", "", clean)
        clean = _re.sub(r"-{3,}", "", clean)
'''
    
    new_content = content[:line_start] + replacement + content[end_idx:]
    with open(path, "w") as f:
        f.write(new_content)
    print("FIXED successfully")
else:
    print(f"Markers not found: start={start_idx}, end={end_idx}")

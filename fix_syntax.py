with open("simulation.py", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    # Detect the split f-string statement
    if 'print(f"' in lines[i] and i + 1 < len(lines) and '[CRITICAL' in lines[i + 1]:
        indent = len(lines[i]) - len(lines[i].lstrip())
        # Reconstruct into a perfectly safe, single-line statement
        new_lines.append(" " * indent + "print(f'\\n[CRITICAL ENGINE ERROR]: {e}'); import traceback; traceback.print_exc()\n")
        i += 2  # Skip both broken lines
    else:
        new_lines.append(lines[i])
        i += 1

with open("simulation.py", "w") as f:
    f.writelines(new_lines)

print("Syntax layout successfully repaired!")

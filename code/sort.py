input_file = "output.txt"
output_file = "output.txt"

# Read lines and strip trailing newlines
with open(input_file, "r", encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]

# Sort first by length, then alphabetically
lines.sort(key=lambda line: (len(line), line))

# Write back, adding newline
with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

def parse_line(line):
    clean = line.split("#", 1)[0].strip()
    if not clean:
        return None
    key, value = clean.split("=", 1)
    return key.strip(), value.strip().strip('"')

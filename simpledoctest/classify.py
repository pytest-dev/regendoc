

def classify(lines):
    first = lines[0]
    content = ''.join(lines[1:])
    if first.startswith('# content of'):
        target = first.strip().split()[-1]
        return 'write', target, content
    elif first[0] == '$':
        cmd = first[1:].strip()
        return 'shell', cmd, content

    return None, first, content

    

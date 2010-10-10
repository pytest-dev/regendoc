

def classify(lines, indent=4, lineno=None):
    first = lines[0]
    content = ''.join(lines[1:])
    
    def at(action, target):
        return {
            'action': action,
            'target': target,
            'content': content,
            'indent': indent,
            'lineno': lineno,
        }


    if first.startswith('# content of'):
        target = first.strip().split()[-1]
        return at('write', target)
    elif first[0] == '$':
        cmd = first[1:].strip()
        return at('shell', cmd)

    return at(None, first)

    

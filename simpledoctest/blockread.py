

def dedent(line, last_indent):
    if last_indent is not None:
        if line[:last_indent].isspace():
            return last_indent, line[last_indent:]
    stripped = line.lstrip(' ')
    return len(line) - len(stripped), stripped

def blocks(lines):
    result = []
    firstline = None
    last_indent = None
    items = []
    for lineno, line in enumerate(lines):

        indent, rest = dedent(line, last_indent)

        if last_indent is None:
            last_indent = indent

        if firstline is None:
            firstline = lineno

        if indent != last_indent:
            if items[0] == '\n':
                del items[0]
                firstline+=1
            if items and items[-1] == '\n':
                del items[-1]
            result.append((last_indent, firstline, items))
            items = [rest]
            last_indent = indent
            firstline = lineno

        else:
            last_indent = indent
            items.append(rest or '\n')

    else:
        result.append((indent, firstline, items))


    return result


def correct_content(content, updates):

    lines = content.splitlines(True)
    for update in reversed(updates):
        line = update['line']
        old_lines = len(update['content'].splitlines())
        indent = ' '*update['indent']
        new_lines = [ indent + _line for _line in update['new_content'].splitlines(1)]
        import pprint
        pprint.pprint(locals())

        lines[line+1: line+old_lines+1] = new_lines


    return ''.join(lines)

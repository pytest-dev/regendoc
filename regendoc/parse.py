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
                firstline += 1
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
        try:
            result.append((indent, firstline, items))
        except UnboundLocalError:
            pass
    return result


def correct_content(content, updates):

    lines = list(content)
    for update in reversed(updates):
        line = update['line']
        old_lines = len(update['content'].splitlines())
        indent = ' ' * update['indent']
        new_lines = [indent + _line
                     for _line in update['new_content'].splitlines(1)]
        lines[line + 1:line + old_lines + 1] = new_lines

    return lines


def classify(lines, indent=4, line=None):
    if not lines:
        return {'action': None}
    first = lines[0]
    content = ''.join(lines[1:])

    def at(action, target, cwd=None):
        return {
            'action': action,
            'cwd': cwd,
            'target': target,
            'content': content,
            'indent': indent,
            'line': line,
        }

    if first.startswith('# content of'):
        target = first.strip().split()[-1]
        return at('write', target)
    elif first[0] == '$':
        cmd = first[1:].strip()
        return at('shell', cmd)
    elif ' $ ' in first:
        cwd, target = first.split(' $ ')
        target = target.strip()
        return at('shell', target, cwd)
    elif not indent and any(x.strip() == '.. regendoc:wipe' for x in lines):
        return {'action': 'wipe'}

    return at(None, first)


def parse_actions(lines, **kw):
    for indent, line, data in blocks(lines):
        mapping = classify(lines=data, indent=indent, line=line)
        mapping.update(kw)
        if mapping['action']:  # None if no idea
            yield mapping

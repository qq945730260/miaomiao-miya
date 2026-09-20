path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v6\server.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines are 0-indexed, so line 173 is index 172
# Current broken lines 172-174 (0-indexed): 172, 173, 174
# Need to fix indentation

new_lines = []
for i, line in enumerate(lines):
    lineno = i + 1
    # Fix lines 173-174: change from 16-space to 12-space indent
    if lineno == 173 and line.strip().startswith('print(f"Storage upload'):
        new_lines.append('        with urllib.request.urlopen(req, timeout=30) as resp:\n')
        new_lines.append('            print(f"Storage upload status: {resp.status}", flush=True)\n')
        new_lines.append('            return safe_name\n')
    elif lineno == 174:
        # Skip this line (replaced by above)
        pass
    elif lineno == 175 and 'except urllib.error.HTTPError' in line:
        # Change from 8-space to 4-space indent
        new_lines.append(line.replace('        except urllib.error.HTTPError', '    except urllib.error.HTTPError'))
    elif lineno == 176 and 'err_body' in line:
        new_lines.append(line.replace('            err_body', '        err_body'))
    elif lineno == 177 and 'print(f"Storage HTTP error' in line:
        new_lines.append(line.replace('            print', '        print'))
    elif lineno == 178 and 'except Exception as e:' in line:
        new_lines.append(line.replace('        except Exception', '    except Exception'))
    elif lineno == 179 and 'print(f"Storage error' in line:
        new_lines.append(line.replace('            print', '        print'))
    elif lineno == 180 and '# Fallback to local upload' in line:
        new_lines.append(line.replace('        # Fallback', '    # Fallback'))
    elif lineno == 181 and 'ext2' in line:
        new_lines.append(line.replace('        ext2', '    ext2'))
    elif lineno == 182 and 'safe_name = secrets' in line and 'ext2' not in line:
        new_lines.append(line.replace('        safe_name', '    safe_name'))
    elif lineno == 183 and 'os.makedirs' in line and 'UPLOAD_DIR' in line:
        new_lines.append(line.replace('        os.makedirs', '    os.makedirs'))
    elif lineno == 184 and 'with open(os.path.join(UPLOAD_DIR' in line:
        new_lines.append(line.replace('        with open', '    with open'))
    elif lineno == 185 and 'f.write(file_bytes.rstrip' in line:
        new_lines.append(line.replace('            f.write', '        f.write'))
    elif lineno == 186 and 'print(f"Fallback' in line:
        new_lines.append(line.replace('        print', '    print'))
    elif lineno == 187 and 'return sn' in line and 'Fallback' not in lines[i-1] if i > 0 else False:
        new_lines.append(line.replace('        return sn', '    return sn'))
    elif lineno == 188 and 'except Exception as e:' in line:
        new_lines.append(line.replace('    except Exception', 'except Exception'))
    elif lineno == 189 and 'print(f"Upload error' in line:
        new_lines.append(line.replace('        print', '    print'))
    elif lineno == 190 and 'ext = os.path.splitext' in line:
        new_lines.append(line.replace('        ext', '    ext'))
    elif lineno == 191 and 'safe_name = secrets' in line and 'ext' in line:
        new_lines.append(line.replace('        safe_name', '    safe_name'))
    elif lineno == 192 and 'os.makedirs' in line and 'UPLOAD_DIR' in line:
        new_lines.append(line.replace('        os.makedirs', '    os.makedirs'))
    elif lineno == 193 and 'with open(os.path.join(UPLOAD_DIR' in line:
        new_lines.append(line.replace('        with open', '    with open'))
    elif lineno == 194 and 'f.write(file_bytes.rstrip' in line:
        new_lines.append(line.replace('            f.write', '        f.write'))
    elif lineno == 195 and 'return sn' in line:
        new_lines.append(line.replace('        return sn', '    return sn'))
    elif lineno == 196:
        # Skip duplicate return sn
        pass
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Fix applied')

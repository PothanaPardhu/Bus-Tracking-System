import pathlib
import re
path = pathlib.Path(r'C:\Users\HP\Downloads\MIPL-PMJ-25037 QR SCAN BASED INTELLIGENT SYSTEM FOR SCHOOL BUS TRACKING\assets\template\user\user-tracking-realtime.html')
text = path.read_text(encoding='utf-8')
script = text.split('<script>')[1].split('</script>')[0]
script = re.sub(r"{{[^}]*}}", "0", script)
# naive brace balance ignoring quotes
open_braces=0
close_braces=0
stack=[]
for i,c in enumerate(script):
    if c=='{':
        open_braces+=1
        stack.append((i,'{'))
    elif c=='}':
        close_braces+=1
        if stack and stack[-1][1]=='{':
            stack.pop()
        else:
            stack.append((i,'}'))
print('open',open_braces,'close',close_braces,'unmatched stack',len(stack))
if stack:
    idx=stack[0][0]
    print('first unmatched index', idx)
    print('context around unmatched:')
    print(script[idx-100:idx+100])
print('length', len(script))

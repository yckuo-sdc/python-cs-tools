import os
import yara

def scan_dir(dir_source, rules): # working
    match_list = []
    for folder,subfolders, files in os.walk(dir_source):
        for file in files:
            path = os.path.join(folder, file)
            try:
                file_name, file_extension = os.path.splitext(file)
                if (file_extension == '.txt' or file_extension == '.php'):
                    with open(path) as f:
                        matches = rules.match(data=f.read(), externals={'filename': file})
                    if len(matches) > 0:
                        matches.append(file)
                        match_list.append(matches)
            except Exception as e:
                print(e)
                pass
    return match_list


rules = yara.compile('/home/yckuo/apps/yararules/webshells_index.yar')
dir_source = '/home/yckuo/apps/webshell/caidao-shell/'

matches = scan_dir(dir_source, rules);
print(matches)

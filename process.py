import psutil
import platform

'''
This script is to assist in finding secondary processes spawned by an initial process.
The keyword is found within the files opened within the secondary process.
In the below example Minecraft Launcher spawns java after the play button is hit.

The keyword is also minecraft because the files opened are in a folder called .minecraft
if you aren't sure what the keyword is turn on debug in the below function.
'''

def find_process_pid(process_name, keyword=None, debug=False):
    proc_found = False
    procs = {p.pid: p.info for p in psutil.process_iter(['pid','name'])}
    for proc in procs:
        if debug:
            print(f"Process {procs[proc]['name']} pid {procs[proc]['pid']}")

        if process_name in procs[proc]['name'] and not keyword:
            return procs[proc]['pid']
        if process_name in procs[proc]['name'] and keyword:
            process_pid = psutil.Process(procs[proc]['pid'])
            pid_files_open = process_pid.open_files()
            for one_file in pid_files_open:
                if debug:
                    print(f'{one_file}')

                if keyword in one_file.path and not debug:
                    return procs[proc]['pid'] 
    if not proc_found:
        return -1

if platform.system() == 'Linux':
    pid = find_process_pid('minecraft')
    pid2 = find_process_pid('java', 'minecraft') # will only show if you hit play else is -1
    print(pid, pid2)
elif platform.system() == 'Windows':
    pid = find_process_pid('MinecraftLauncher.exe')
    pid2 = find_process_pid('javaw', 'minecraft') # will only show if you hit play else is -1
    print(pid, pid2)
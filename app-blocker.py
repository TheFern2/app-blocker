import requests, argparse, string, random, configparser, os, random
from pathlib import Path
from shutil import copy, rmtree
import datetime, time
import platform
import psutil
from tkinter import Tk
import tkinter.messagebox
import threading
from pathlib import Path

if platform.system() == 'Windows':
    import win32com.client

# global variables
num_letters = 1
nested_levels = 10
move_path = ''
add_random_files_count = 0
popup_path = ''
show_icon = False
home_path = str(Path.home()) # Users home path to store settings under .config/app-blocker/
app_blocker_path = os.path.abspath(__file__) # might not need this
app_blocker_dir = os.path.dirname(app_blocker_path) # might not need this
obs_paths = configparser.ConfigParser()
obs_paths.read('obs-paths.conf')
states = configparser.ConfigParser()

def show_popup(message):
    root = tkinter.Tk()
    root.wm_withdraw()
    tkinter.messagebox.showwarning('App Blocker Warning', message)
    root.destroy()

def time_delay(secs):
    time.sleep(secs)

def get_random_path():
    random_path = '/'

    for _ in range(nested_levels):
        for _ in range(num_letters):
            curr_letter = random.choice(string.ascii_lowercase)
            random_path += curr_letter
        random_path += '/'
    #print(random_path)
    return random_path

def get_random_filename():
    random_filename = ''
    for _ in range(6):
        curr_letter = random.choice(string.ascii_lowercase)
        random_filename += curr_letter
    return random_filename

def split_parameters(input):
    list_parameters = []
    first_split = input.split(',')
    for params in first_split:
        second_split = params.split('|')
        temp_list = []
        for param in second_split:            
            temp_list.append(param)
        list_parameters.append(temp_list)
    return list_parameters


# time slot is a list, list[0] starting time, and list[1] ending time
def are_you_on_break(current_time, time_slot):
    starting_break = int(time_slot[0])
    ending_break = int(time_slot[1])
    if current_time >= starting_break and current_time <= ending_break:
        return True
    else:
        return False


# extra binaries will be special cases, so better to be added manually to config
# def add_file_to_config(filename, extra_bin=None, attached_bin=None, shortcut_path=None):
def add_file_to_config(filename, shortcut_path=None):
    if os.path.isfile(filename):
        # check if filename is in obs-paths.conf
        section_name = os.path.basename(filename)
        if not obs_paths.has_section(section_name):
            obs_paths.add_section(section_name)

        if obs_paths.has_section(section_name):
            obs_paths.set(section_name, 'full-path', filename)
            obs_paths.set(section_name, 'file-size-bytes', str(os.path.getsize(filename)))

            if shortcut_path and platform.system() != 'Darwin':
                if os.path.isfile(shortcut_path):
                    obs_paths.set(section_name, 'shortcut-path', shortcut_path)

                    if platform.system() == 'Linux':
                        desktop = configparser.ConfigParser()
                        desktop.read(shortcut_path)
                        if desktop.has_option('Desktop Entry', 'Exec'):
                            exec_path = desktop.get('Desktop Entry', 'Exec')
                            obs_paths.set(section_name, 'shortcut-target', exec_path)

                    if platform.system() == 'Windows':
                        shell = win32com.client.Dispatch('WScript.Shell')
                        shortcut = shell.CreateShortcut(shortcut_path) # windows lnk
                        obs_paths.set(section_name, 'shortcut-target', shortcut.TargetPath)
                        

            file = open('obs-paths.conf', 'w+')
            obs_paths.write(file)
            file.close()

    else:
        print('File does not exist')


def remove_file_from_config(filename):
    section_name = os.path.basename(filename)
    if obs_paths.has_section(section_name):
        obs_paths.remove_section(section_name)
        file = open('obs-paths.conf', 'w+')
        obs_paths.write(file)
        file.close()


def find_process_pid(process_name, keyword=None):
    proc_found = False
    procs = {p.pid: p.info for p in psutil.process_iter(['pid','name'])}
    for proc in procs:
        if process_name in procs[proc]['name'] and not keyword:
            return procs[proc]['pid']
        if process_name in procs[proc]['name'] and keyword:
            process_pid = psutil.Process(procs[proc]['pid'])
            pid_files_open = process_pid.open_files()
            for one_file in pid_files_open:
                if keyword in one_file.path:
                    return procs[proc]['pid'] 
    if not proc_found:
        return -1


def write_shebang(filename):
    tempfile = filename + '.bak'
    with open(filename, 'r') as read_obj, open(tempfile, 'w') as write_obj:
        write_obj.write('#!/usr/bin/env xdg-open\n')
        all_lines = read_obj.readlines()
        write_obj.writelines(all_lines)
    os.remove(filename)
    os.rename(tempfile, filename)


def point_to_popup(filename, icon_path=None):
    if platform.system() == 'Linux':
        desktop = configparser.ConfigParser()
        desktop.optionxform = str
        desktop.read(filename)
        if desktop.has_option('Desktop Entry', 'Exec'):
            desktop.set('Desktop Entry', 'Exec', 'python3 ' + popup_path)
            file = open(filename, 'w+')
            desktop.write(file, space_around_delimiters=False)
            file.close()
            write_shebang(filename)
    elif platform.system() == 'Windows':
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(filename)
        #icon_path = shortcut.TargetPath
        shortcut.TargetPath = popup_path
        if show_icon:
            shortcut.IconLocation = f'{icon_path},0'
        shortcut.Save()

def point_to_original(filename, shortcut_target):
    if platform.system() == 'Linux':
        desktop = configparser.ConfigParser()
        desktop.optionxform = str
        desktop.read(filename)
        if desktop.has_option('Desktop Entry', 'Exec'):
            desktop.set('Desktop Entry', 'Exec', shortcut_target)
            file = open(filename, 'w+')
            desktop.write(file, space_around_delimiters=False)
            file.close()
            write_shebang(filename)
    elif platform.system() == 'Windows':
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(filename)
        shortcut.TargetPath = shortcut_target
        if show_icon:
            shortcut.IconLocation = f'{shortcut_target},0'
        shortcut.Save()


def obsfucate_files():
    obs_paths.read('obs-paths.conf') # might be irrelevant call, called at the top
    obs_sections = obs_paths.sections()
    # print(f"Number of sections in obs-paths {len(obs_sections)}")
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')

        ######### TESTING ###########
        # check if binary process is active i.e running
        # give user 3 minutes to exit
        # then continue obsfucation
        is_main_binary_running = False
        is_extra_binary_running = False
        is_attached_binary_running = False
        binary_name = os.path.basename(original_filename_path)
        main_binary_pid = find_process_pid(binary_name)

        # check here for extra binaries or attach binaries
        # ['binary|obsfuscate 0 or 1(bool)] <- extra-bin
        # ['binary|keyword|obsfuscate(bool)] <- attached-bin

        # test variable
        #attached_bin = find_process_pid('java', 'minecraft')
        
        #print(f'Binary PID {main_binary_pid} Attached PID {attached_bin}')
        ## Check if main binary, extra or attached binaries are running

        if main_binary_pid != -1:
            is_main_binary_running = True
            
            # if psutil.Process(main_binary_pid).status() == psutil.STATUS_RUNNING:
            #     psutil.Process(main_binary_pid).kill()
            
            # proc_two = psutil.Process(attached_bin).kill()

        if obs_paths.has_option(section, 'extra-bin'):
            extra_bin = obs_paths.get(section, 'extra-bin')
            extra_bin_parameters = split_parameters(extra_bin)
            for index in range(len(extra_bin_parameters)):
                # for now [index][1] obsfucate option will not be used
                extra_binary_pid = find_process_pid(extra_bin_parameters[index][0])
                if extra_binary_pid != -1 and not is_extra_binary_running:
                    is_extra_binary_running = True

        if obs_paths.has_option(section, 'attached-bin'):
            attached_bin = obs_paths.get(section, 'attached-bin')
            attached_bin_parameters = split_parameters(attached_bin)
            for index in range(len(attached_bin_parameters)):
                # for now [index][2] obsfucate option will not be used
                attached_binary_pid = find_process_pid(attached_bin_parameters[index][0], attached_bin_parameters[index][1])
                if attached_binary_pid != -1 and not is_attached_binary_running:
                    is_attached_binary_running = True
        
        
        if is_main_binary_running or is_extra_binary_running or is_attached_binary_running:
            # show popup for user to exit program
            # TODO need this popup on another thread to avoid locking this script
            # or else user can ignore popup and processes will never be closed

            # start sleep on a separate thread
            t1 = threading.Thread(target=time_delay, name='thread1', args= [90])
            t2 = threading.Thread(
                target=show_popup, name='thread2', args= ['Please save games, games will be exiting in 3 minutes'])
            t1.start()
            t2.start()
            t1.join()

            # show_popup('Please save games, games will be exiting in 3 minutes')
            # time.sleep(180)

        ## Kill binaries here if they are still running
        if is_main_binary_running:
            main_binary_pid = find_process_pid(binary_name)
            if main_binary_pid != -1:
                psutil.Process(main_binary_pid).kill()
                print(f'Main binary killed {main_binary_pid}')

        if is_extra_binary_running:
            for index in range(len(extra_bin_parameters)):
                # for now [index][1] obsfucate option will not be used
                extra_binary_pid = find_process_pid(extra_bin_parameters[index][0])
                if extra_binary_pid != -1:
                    psutil.Process(extra_binary_pid).kill()
                    print('Extra binary killed')

        if is_attached_binary_running:
            for index in range(len(attached_bin_parameters)):
                # for now [index][2] obsfucate option will not be used
                attached_binary_pid = find_process_pid(attached_bin_parameters[index][0], attached_bin_parameters[index][1])
                if attached_binary_pid != -1:
                    psutil.Process(attached_binary_pid).kill()
                    print(f'Attached binary killed {attached_binary_pid}')

        ################################

        random_filename = get_random_filename()
        random_path = get_random_path()

        # file randomization
        if not os.path.exists(move_path):
            os.makedirs(move_path)
        if not os.path.exists(move_path + random_path):
            os.makedirs(move_path + random_path)

        if platform.system() == 'Windows':
            extension_split = binary_name.split('.')
            binary_extension = extension_split[-1]
            try:
                copy(original_filename_path, move_path + random_path + random_filename + '.' + binary_extension)
            except IOError as e:
                print(f'File not copied in obsfucate function\n {e}')

        if platform.system() == 'Linux':
            try:
                copy(original_filename_path, move_path + random_path + random_filename)
            except IOError as e:
                print(f'File not copied in obsfucate function\n {e}')

        # shortcut if it exists, and not mac osx
        if obs_paths.has_option(section, 'shortcut-path') and platform.system() != 'Darwin':
            shortcut_path = obs_paths.get(section, 'shortcut-path')
            # we want to modify shortcut target to popup.py
            # file.desktop file for linux
            # shortcut.lnk for windows
            # need to work on mac later on
            if platform.system() == 'Linux':
                point_to_popup(shortcut_path)
            elif platform.system() == 'Windows':
                # windows icon needs original icon on .exe
                # might need to add an option to leave icon alone, then it will just show white
                # knowing how to edit shortcut icon properties could lead to original exe
                icon_path = move_path + random_path + random_filename + '.' + binary_extension
                point_to_popup(shortcut_path, icon_path)
                #print(move_path + random_path + random_filename + '.' + binary_extension)
            elif platform.system() == 'Darwin':
                pass
        
        # check if file was indeed copied and then delete
        if (os.path.isfile(move_path + random_path + random_filename) or
            platform.system() == 'Windows' and os.path.isfile(move_path + random_path + random_filename + '.' + binary_extension)):
            os.remove(original_filename_path)

            if platform.system() == 'Linux':
                # update conf with random path
                obs_paths.set(section, 'random-path', move_path + random_path + random_filename)
            elif platform.system() == 'Windows':
                obs_paths.set(section, 'random-path', move_path + random_path + random_filename + '.' + binary_extension)            

            file = open('obs-paths.conf', 'w+')
            obs_paths.write(file)
            file.close()
        else:
            print('File was not removed!')


def add_random_files():
    # for each file in obs-paths random paths will be created
    # depending on add-random-files-count
    obs_sections = obs_paths.sections()
    for section in obs_sections:
        obfuscated_size = obs_paths.getint(section, 'file-size-bytes')
        # create at least one identical size
        random_filename = get_random_filename()
        random_path = get_random_path()
        if not os.path.exists(move_path + random_path):
            os.makedirs(move_path + random_path)
        with open(move_path + random_path + random_filename, 'wb') as fout:
            fout.write(os.urandom(obfuscated_size))

        # create some random files, with random size based on original size    
        for _ in range(add_random_files_count):
            random_filename = get_random_filename()
            random_path = get_random_path()
            if not os.path.exists(move_path + random_path):
                os.makedirs(move_path + random_path)
            with open(move_path + random_path + random_filename, 'wb') as fout:
                fout.write(os.urandom(random.randrange(obfuscated_size)))
    

def restore_files():
    obs_paths.read('obs-paths.conf')
    obs_sections = obs_paths.sections()
    all_files_moved = True
    # print(len(obs_sections))
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        obfuscated_path = obs_paths.get(section, 'random-path')
        try:
            copy(obfuscated_path, original_filename_path)
        except IOError as e:
            print(f'File not copied in restore function\n {e}')

        # shortcut if it exists
        if obs_paths.has_option(section, 'shortcut-path'):
            shortcut_path = obs_paths.get(section, 'shortcut-path')
            shortcut_target = obs_paths.get(section, 'shortcut-target')
            # we want to modify shortcut target to popup.py
            # file.desktop file for linux
            # shortcut.lnk for windows
            # need to work on mac later on
            if platform.system()  == 'Linux' or platform.system()  == 'Windows':
                point_to_original(shortcut_path, shortcut_target)
            elif platform.system()  == 'Darwin':
                pass
    
    # Delete all directories under move_path
    # Ensure all original files are in full-path
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        if not os.path.exists(original_filename_path):
            all_files_moved = False        

    if all_files_moved:
        rmtree(move_path)

        # check if file exists and if it has section then read state
        if os.path.exists('states.conf'):
            states.read('states.conf')
            if states.has_section('States'):
                states.set('States', 'block-apps', 'False')
                states.set('States', 'obsfucation-ran', 'False')
                file = open('states.conf', 'w+')
                states.write(file)
                file.close()
        else:
            states.add_section('States')
            states.set('States', 'block-apps', 'False')
            states.set('States', 'obsfucation-ran', 'False')
            file = open('states.conf', 'w+')
            states.write(file)
            file.close()


def main():
    global num_letters, move_path, nested_levels, add_random_files_count, popup_path, show_icon

    parser = argparse.ArgumentParser()
    parser.add_argument('--add-binary-path', help='Add path to a binary or executable')
    parser.add_argument('--remove-binary-path', help='Remove path to a binary or executable')
    parser.add_argument('--add-shortcut-path')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--recover', action='store_true')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('app-blocker.conf')

    move_path = config.get('Settings', 'move-path')    
    nested_levels = config.getint('Settings', 'nested-levels')
    num_letters = config.getint('Settings', 'num-letters')
    add_random_files_count = config.getint('Settings', 'add-random-files-count')
    get_server_permission_url = config.get('Settings', 'get-server-permission')
    set_server_permission_url = config.get('Settings', 'set-server-permission')
    use_server = config.getboolean('Settings', 'use-server')
    popup_path = config.get('Settings', 'popup-path')
    show_icon = config.getboolean('Settings', 'show-icon')
    breaks = config.get('Settings', 'breaks')
    breaks_list = split_parameters(breaks)

    # cli arguments input getting messy :(
    # extra binaries and attached + breaks
    # might be better just as config parameters and not cli
    if args.add_binary_path and args.add_shortcut_path:
        add_file_to_config(args.add_binary_path, args.add_shortcut_path)
    elif args.add_binary_path:
        add_file_to_config(args.add_binary_path)
    elif args.remove_binary_path:
        remove_file_from_config(args.remove_binary_path)
    elif args.recover:
        restore_files()

    obs_sections = obs_paths.sections()
    if len(obs_sections) == 0:
        print('Check cli options with --help, no binary paths found in configuration.')
        print('Exiting...')
        exit()

    start_time = config.getint('Settings', 'start-time')
    stop_time = config.getint('Settings', 'stop-time')
    block_apps = False
    obsfucation_ran = False
    #break_ran = False
    on_break = False

    # check if file exists and if it has section then read state
    if os.path.exists('states.conf'):
        states.read('states.conf')
        if states.has_section('States'):
            block_apps = states.getboolean('States', 'block-apps')
            obsfucation_ran = states.getboolean('States', 'obsfucation-ran')
    else:
        states.add_section('States')
        states.set('States', 'block-apps', str(block_apps))
        states.set('States', 'obsfucation-ran', str(obsfucation_ran))
        file = open('states.conf', 'w+')
        states.write(file)
        file.close()

    if args.run:
        print('Service started...')
        # do not obsfuscate if move_path folder exists and is not empty
        # check if file exists and if it has section then read state
        if os.path.exists(move_path):
            print('Move path exists, please run recover command.')
            exit()


    while args.run:
        block_apps_state = block_apps
        now = datetime.datetime.now()
        current_time = int(now.strftime('%H%M'))
        server_permission = -1
        

        # check if is break time already
        if current_time >= start_time and current_time < stop_time:
            for lunch_break in breaks_list:
                on_break = are_you_on_break(current_time, lunch_break)
                #print(f'On Break {on_break}')

        # only look at server inside school time, irgnore rest of the day
        if current_time >= start_time and current_time < stop_time and use_server:
            try:
                receive = requests.get(f'http://{get_server_permission_url}')
                server_permission = int(receive.text)
            except requests.exceptions.RequestException:
                print(f'Server not online, make sure is online or disable in config!')

        # print(f'Obs Ran {obsfucation_ran} On Break {on_break}')
        if (current_time >= start_time and current_time < stop_time and not obsfucation_ran and not on_break or 
            server_permission == 1 and not obsfucation_ran):

            obsfucate_files()
            add_random_files()
            block_apps = True
            obsfucation_ran = True
            # update states
            states.read('states.conf')
            states.set('States', 'block-apps', str(block_apps))
            states.set('States', 'obsfucation-ran', str(obsfucation_ran))
            file = open('states.conf', 'w+')
            states.write(file)
            file.close()

        if (current_time > start_time and current_time >= stop_time and obsfucation_ran or
            current_time > start_time and current_time <= stop_time and obsfucation_ran and on_break or
            server_permission == 0 and obsfucation_ran):

            block_apps = False
            restore_files()
            obsfucation_ran = False
            # update states
            states.read('states.conf')
            states.set('States', 'block-apps', str(block_apps))
            states.set('States', 'obsfucation-ran', str(obsfucation_ran))
            file = open('states.conf', 'w+')
            states.write(file)
            file.close()

        if current_time == stop_time + 1 and use_server:
            requests.post(f'http://{set_server_permission_url}1')

        # only log if there is a change
        if block_apps != block_apps_state:
            print(f'Block App State: {block_apps}, Time: {current_time}, Break Status: {on_break}')

        time.sleep(3) # a small time delay to avoid excessive server calls
        

if __name__ == '__main__':
    main()

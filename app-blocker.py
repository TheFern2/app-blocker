import requests, argparse, string, random, configparser, os, random
from pathlib import Path
from shutil import copy, rmtree
import datetime, time
import platform
import psutil
from tkinter import Tk
import tkinter.messagebox

# global variables
num_letters = 1
nested_levels = 10
move_path = ''
add_random_files_count = 0
popup_shortcut = ''
obs_paths = configparser.ConfigParser()
obs_paths.read('obs-paths.conf')
states = configparser.ConfigParser()

def show_popup(message):
    root = tkinter.Tk()
    root.wm_withdraw()
    tkinter.messagebox.showwarning('App Blocker Warning', message)
    root.destroy()

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

def add_file_to_config(filename, extra_bin=None, attached_bin=None, shortcut_path=None):
    if os.path.isfile(filename):
        # check if filename is in obs-paths.conf
        section_name = os.path.basename(filename)
        if not obs_paths.has_section(section_name):
            obs_paths.add_section(section_name)
            obs_paths.set(section_name, 'full-path', filename)
            obs_paths.set(section_name, 'file-size-bytes', str(os.path.getsize(filename)))

            if extra_bin:
                obs_paths.set(section_name, 'extra-bin', extra_bin)
            if attached_bin:
                obs_paths.set(section_name, 'attached-bin', attached_bin)

            if shortcut_path and platform.system() != 'Darwin': # shortcuts not supported for mac 
                if os.path.isfile(shortcut_path):
                    obs_paths.set(section_name, 'shortcut-path', shortcut_path)

            file = open('obs-paths.conf', 'w+')
            obs_paths.write(file)
            file.close()

        if obs_paths.has_section(section_name) and shortcut_path and platform.system() != 'Darwin':
            if os.path.isfile(shortcut_path):
                obs_paths.set(section_name, 'shortcut-path', shortcut_path)
                if extra_bin:
                    obs_paths.set(section_name, 'extra-bin', extra_bin)
                if attached_bin:
                    obs_paths.set(section_name, 'attached-bin', attached_bin)
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
        binary_name = os.path.basename(original_filename_path)
        main_binary_pid = find_process_pid(binary_name)

        # check here for extra binaries or attach binaries
        # ['binary|obsfuscate(bool)] <- extra-bin
        # ['binary|keyword|obsfuscate(bool)] <- attached-bin

        # test variable
        attached_bin = find_process_pid('java', 'minecraft')

        print(f'Binary PID {main_binary_pid} Attached PID {attached_bin}')

        if main_binary_pid != -1 or attached_bin != -1:
            # show popup for user to exit program
            show_popup('Please save games, games will be exiting in 3 minutes')
            time.sleep(180)
            proc_one = psutil.Process(main_binary_pid).kill()
            proc_two = psutil.Process(attached_bin).kill()

        ################################

        random_filename = get_random_filename()
        random_path = get_random_path()

        # file randomization
        if not os.path.exists(move_path):
            os.makedirs(move_path)
        if not os.path.exists(move_path + random_path):
            os.makedirs(move_path + random_path)
        copy(original_filename_path, move_path + random_path + random_filename)

        # shortcut if it exists, and not mac osx
        if obs_paths.has_option(section, 'shortcut-path') and platform.system() != 'Darwin':
            shortcut_path = obs_paths.get(section, 'shortcut-path')
            random_shortcut = get_random_filename()
            copy(shortcut_path, move_path + random_path + random_shortcut)
            # check if file was indeed copied and then delete
            if os.path.isfile(move_path + random_path + random_shortcut):
                os.remove(shortcut_path)
                copy(popup_shortcut, shortcut_path)
                obs_paths.set(section, 'random-shortcut-path', move_path + random_path + random_shortcut)     
        
        # check if file was indeed copied and then delete
        if os.path.isfile(move_path + random_path + random_filename):
            os.remove(original_filename_path)

            # update conf with random path
            obs_paths.set(section, 'random-path', move_path + random_path + random_filename)
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
        copy(obfuscated_path, original_filename_path)

        # shortcut if it exists
        if obs_paths.has_option(section, 'random-shortcut-path'):
            shortcut_path = obs_paths.get(section, 'shortcut-path')
            random_shortcut_path = obs_paths.get(section, 'random-shortcut-path')
            copy(random_shortcut_path, shortcut_path)

            if not os.path.exists(shortcut_path):
                all_files_moved = False
    
    # Delete all directories under move_path
    # Ensure all original files are in full-path
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        if not os.path.exists(original_filename_path):
            all_files_moved = False        

    if all_files_moved:
        rmtree(move_path)


def main():
    global num_letters, move_path, nested_levels, add_random_files_count, popup_shortcut

    parser = argparse.ArgumentParser()
    parser.add_argument('--add-binary-path', help='Add path to a binary or executable')
    parser.add_argument('--remove-binary-path', help='Remove path to a binary or executable')
    parser.add_argument('--add-shortcut-path')
    parser.add_argument('--add-extra-binaries', help='Extra processes spawned by main binary, i.e. \'binary|obsfuscate(bool)\',...')
    parser.add_argument('--add-attached-binaries', help='Extra system processes spawned by main binary, i.e. \'binary|keyword|obsfuscate(bool)\',...')
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
    popup_shortcut = config.get('Settings', 'popup-shortcut')

    # cli arguments input getting messy :(
    # extra binaries and attached + breaks
    # might be better just as config parameters and not cli
    if args.add_binary_path and args.add_extra_binaries and args.add_attached_binaries and args.add_shortcut_path:
        add_file_to_config(args.add_binary_path, args.add_extra_binaries, args.add_attached_binaries, args.add_shortcut_path)
    if args.add_binary_path and args.add_extra_binaries and args.add_attached_binaries:
        add_file_to_config(args.add_binary_path, args.add_extra_binaries, args.add_attached_binaries, None)
    if args.add_binary_path and args.add_attached_binaries:
        add_file_to_config(args.add_binary_path, None, args.add_attached_binaries, None)
    if args.add_binary_path and args.add_extra_binaries:
        add_file_to_config(args.add_binary_path, args.add_extra_binaries, None, None)
    if args.add_binary_path and args.add_shortcut_path:
        add_file_to_config(args.add_binary_path, None, None, args.add_shortcut_path)
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

        # only look at server inside school time, irgnore rest of the day
        if current_time >= start_time and current_time < stop_time and use_server:
            try:
                receive = requests.get(f'http://{get_server_permission_url}')
                server_permission = int(receive.text)
            except requests.exceptions.RequestException:
                print(f'Server not online, make sure is online or disable in config!')

        if current_time >= start_time and current_time < stop_time and not obsfucation_ran or server_permission == 0 and not obsfucation_ran:
            add_random_files()
            obsfucate_files()
            block_apps = True
            obsfucation_ran = True
            # update states
            states.read('states.conf')
            states.set('States', 'block-apps', str(block_apps))
            states.set('States', 'obsfucation-ran', str(obsfucation_ran))
            file = open('states.conf', 'w+')
            states.write(file)
            file.close()

        if current_time > start_time and current_time >= stop_time and obsfucation_ran or server_permission == 1 and obsfucation_ran:
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
            requests.post(f'http://{set_server_permission_url}0')

        # only log if there is a change
        if block_apps != block_apps_state:
            print(f'Block Apps {block_apps} {current_time}')

        time.sleep(3) # a small time delay to avoid excessive server calls
        

if __name__ == '__main__':
    main()

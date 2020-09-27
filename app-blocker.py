import requests, argparse, string, random, configparser, os, random
from pathlib import Path
from shutil import copy, rmtree
import datetime, time

# global variables
num_letters = 1
nested_levels = 10
move_path = ''
add_random_files_count = 0
motd = ''
obs_paths = configparser.ConfigParser()
obs_paths.read('obs-paths.conf')
states = configparser.ConfigParser()


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

def add_file_to_config(filename):
    if os.path.isfile(filename):
        # check if filename is in obs-paths.conf
        section_name = os.path.basename(filename)
        if not obs_paths.has_section(section_name):
            obs_paths.add_section(section_name)
            obs_paths.set(section_name, 'full-path', filename)
            obs_paths.set(section_name, 'file-size-bytes', str(os.path.getsize(filename)))
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

def obsfucate_files():
    obs_paths.read('obs-paths.conf') # might be irrelevant call, called at the top
    obs_sections = obs_paths.sections()
    # print(f"Number of sections in obs-paths {len(obs_sections)}")
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        random_filename = get_random_filename()
        random_path = get_random_path()

        if not os.path.exists(move_path):
            os.makedirs(move_path)
        if not os.path.exists(move_path + random_path):
            os.makedirs(move_path + random_path)
        copy(original_filename_path, move_path + random_path + random_filename)

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
    

def obsfucate_file(filename):
    
    random_filename = get_random_filename()
    random_path = get_random_path()
    if not os.path.exists(move_path):
        os.makedirs(move_path)
    if not os.path.exists(move_path + random_path):
        os.makedirs(move_path + random_path)
    copy(filename, move_path + random_path + random_filename)

    # check if file was indeed copied and then delete
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        print('File was not removed!')

    # check if filename is in obs-paths.conf
    section_name = os.path.basename(filename)
    if not obs_paths.has_section(section_name):
        obs_paths.add_section(section_name)
        obs_paths.set(section_name, 'full-path', filename)
        obs_paths.set(section_name, 'random-path', move_path + random_path + random_filename)
        file = open('obs-paths.conf', 'w+')
        obs_paths.write(file)
        file.close()
    else:
        obs_paths.set(section_name, 'random-path', move_path + random_path + random_filename)
        file = open('obs-paths.conf', 'w+')
        obs_paths.write(file)
        file.close()


def restore_files():
    obs_paths.read('obs-paths.conf')
    obs_sections = obs_paths.sections()
    # print(len(obs_sections))
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        obfuscated_path = obs_paths.get(section, 'random-path')
        copy(obfuscated_path, original_filename_path)
    
    # Delete all directories under move_path
    # Ensure all original files are in full-path
    all_files_moved = True
    for section in obs_sections:
        original_filename_path = obs_paths.get(section, 'full-path')
        if not os.path.exists(original_filename_path):
            all_files_moved = False

    if all_files_moved:
        rmtree(move_path)


def main():
    global num_letters, move_path, nested_levels, add_random_files_count, motd

    parser = argparse.ArgumentParser()
    parser.add_argument('--add-binary-path', help='Add path to a binary or executable')
    parser.add_argument('--remove-binary-path', help='Remove path to a binary or executable')
    parser.add_argument('--run', action='store_true')
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

    if args.add_binary_path:
        add_file_to_config(args.add_binary_path)
    if args.remove_binary_path:
        remove_file_from_config(args.remove_binary_path)

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

    #############################################

    while args.run:
        block_apps_state = block_apps
        now = datetime.datetime.now()
        current_time = int(now.strftime('%H%M'))
        server_permission = -1

        # only look at server inside school time, irgnore rest of the day
        if current_time >= start_time and current_time < stop_time and use_server:
            receive = requests.get(f'http://{get_server_permission_url}')
            server_permission = int(receive.text)

        if current_time >= start_time and current_time < stop_time and not obsfucation_ran or server_permission == 0 and not obsfucation_ran: # add OR for server status
            # print('Block apps ' + str(current_time))
            add_random_files()
            block_apps = True
            obsfucate_files()
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

        if current_time == stop_time + 1:
            if use_server:
                r = requests.post(f'http://{set_server_permission_url}0')

        # only log if there is a change
        if block_apps != block_apps_state:
            print(f'Block Apps {block_apps} {current_time}')

        time.sleep(3) # a small time delay to avoid excessive server calls
        

if __name__ == '__main__':
    main()

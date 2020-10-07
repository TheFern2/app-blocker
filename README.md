# App-Blocker An application to hide pesky games during school time

> NB: Backup binaries and shortcuts, as the app is going through beta and alpha testing. The app has good mechanisms so far to avoid overriding obsfuscated files, and recovering. Will add backup cli command to an external drive later on.

## What does app-blocker do?

This application is meant to be ran as a service this is easy to do in linux, and mac. In Windows there is an application called [NSSM](https://nssm.cc/). I think for now, just give it a try maybe with a chron job on boot to see if you like what it does.

On a high level overview the application takes a number of binary files, and optional shortcuts. Then it obsfuscates those binary files in random nested directories, and randomizes the filename. It will obsfuscate files when is inside the working hours, and not during breaks. I've added an option to use a server to enable or disable the obsfuscation too, in case chores or school work is completed early.

`popup.pyw`, and `server.py` can be completely redone to your liking, as long as server sends 0 to disable and 1 to enable obsfuscation. You can also opt out not to use the server, and completely rely on times.

## Dependencies

- Linux and Mac
    - requests
    - flask
    - psutils

- Windows (same as above plus)
    - pywin32 (Needed for shortcut manipulation)

## Pre-flight checks

Ensure the child account doesn't have admin rights, or sudo access. Or else it can render this app useless by reinstalling software. You also need to make sure you child doesn't have access to all the files in this repo, or that they can't remove them. On Windows just put this repo under your admin account, go into security and make sure your child account doesn't have read or even write to avoid reading configs and code. A clever one can find a few bugs. On Linux the same put this repo under a root account or just check folder permissions too same concept as on Windows.

- Make sure they can't uninstall your cronjob or task schedule
- Make sure they can't install software
- Make sure they can't delete this repo

## Initial Setup

Manually install dependencies with pip. (At a much later date, this will be converted to a pypi package)

### app-blocker.conf

```
[Settings]
add-random-files-count = 3
start-time = 1251
stop-time = 1253
breaks = 1720|1723
num-letters = 4
nested-levels = 3
move-path = /home/fernandob/Documents/Temp/Blocked
popup-path = /home/fernandob/git/app-blocker/popup.pyw
use-server = 0
get-server-permission = 192.168.0.42:3012/permission/Cristy
set-server-permission = 192.168.0.42:3012/permission/Cristy/
show-icon = 0
```
```
add-random-files-count: how many random files it will add per binary
start-time: start time to hide programs in 2400
stop-time = stop time to hide programs in 2400
breaks = breaks to unhide programs one break = 0900|0930 multiple breaks = 0900|0930, 1100|1300
num-letters = number of letters for names of random directories
nested-levels = nested levels of random directories
move-path = where all randomized files will be moved to
popup-path = path to a python file that will show a popup
use-server = if you are using a web server to control the app
get-server-permission = 192.168.0.42:3012/permission/Cristy => returns 0 or 1
set-server-permission = 192.168.0.42:3012/permission/Cristy/ => sets 0 or 1
show-icon = whether to show an icon on windows, see OS differences
```


### Running commands

Examples:
```
app-blocker.py --add-binary-path /path/to/a/binary
app-blocker.py --add-binary-path /path/to/a/binary --add-shortcut-path /path/to/file.desktop
app-blocker.py --remove-binary-path /path/to/a/binary
app-blocker.py --run
app-blocker.py --recover
```

Windows double quotes needed if path contains spaces:
```
app-blocker.py --add-binary-path "C:\Path to\File.exe" --add-shortcut-path "C:\Path to\file.lnk"
```

## Special configuration

> I've included a debugging script `process.py` to help find secondary binaries or attached binaries.

There are some things to be aware of, some applications launch/spawn other processes in certain ocassions. One example of this are games or applications that use java. In this ocassions killing the main binary pid isn't enough, and you'll need to search what are the other processes that need to killed.

I'll talk about minecraft since is a game based on java. When you launch the minecraft launcher, that will be considered the main binary. Once you hit play, a java instance will launch a bunch of minecraft files. It is necessary to know which keyword to search for, or else you could be killing the wrong java instance if you have some other program based on java running.

On Linux, you'll see the processes started for the launcher, then after you hit play, you'll see java with the ps -ef you can see all the files launched: (Note: If you aren't sure what processes your app is spawning, just to ps -e or tasklist on windows)

```
ps -e | grep mine
ps -ef | grep mine
```

On Windows running the launcher will yield the following running tasks:

```
C:\Users\Default.DESKTOP-GU2MB4F>tasklist | findstr "Mine"
MinecraftLauncher.exe         9732 Console                    1    111,652 K
MinecraftLauncher.exe         7884 Console                    1     51,068 K
MinecraftLauncher.exe         7576 Console                    1     76,120 K

```

Once you hit play then a java instance is started, by doing verbose switch we can see that javaw.exe is attached to minecraft:

```
C:\Users\Default.DESKTOP-GU2MB4F>tasklist /v | findstr "javaw"
javaw.exe                     9748 Console                    1  1,548,640 K Running         DESKTOP-GU2MB4F\Default                                 0:00:27 Minecraft 1.16.3
```

## Adding to obs-path.conf

Find the section for that particular binary

Binary|keyword|obsfuscate
```
attached-bin = java|minecraft|0
or
attached-bin = java|minecraft|0, some_bin|keyword|1
```
> The last parameter isn't being used for now.

If there is another processed needed to be killed then use:

```
extra-bin = java|0
or
attached-bin = java|0, some_bin|1
```
> The last parameter isn't being used for now.


## Testing before next step

You'll want to make sure you test to make sure you have all dependencies installed, and no issues with your python install.
Set start time, stop time, and move path at the very least for this test.

```
sudo python3 app-blocker --run
Service started...
Block App State: True, Time: 1844, Break Status: False
Block App State: False, Time: 1845, Break Status: False
```

For initial testing make time a bit larger maybe 10min, then open up the app/apps you are trying to block to make sure they get killed if user decides not to listen to the popup.

You can also add breaks like this:

```
breaks = 1720|1723
or
breaks = 1720|1723, 1500|1600, ...
```

## Running as a Cronjob on linux

You'll want to run crontab -e as root

```
sudo crontab -e
* * * * * cd /home/someUser/git/app-blocker/ && app-blocker.py --run-once
```

## Running as a scheduled task on Windows

For windows is quite easy as well:

Create a app-blocker.bat file, you can add a `pause` if something is failing:

```
cd C:\git\app-blocker
python app-blocker.py --run-once
```

Open task scheduler, create task, give it a name:

- Run whether user is logged on
- Run with highest privileges
- Hidden (Win 10)
- Trigger, run every day, every minute
- Action, start a program, browse to app-blocker.bat file
- On Conditions I unchecked all checkboxes
- Did not change Settings tab

If the task is getting a return error, you must likely missed a step, or missing dependencies.

## OS Differences

Developing an application for multiple OSes is always a pain. The core of the application was pretty solid, but as I started adding features I was aware that I needed to separate items based on OS.

If you only use this for binaries, then all three major OSes, Linux, Windows, and Mac work about the same. When I say binaries it can be anything that can execute.

For the shortcut re-target modification is when things became more complicated for me at least on Debian/Ubuntu shortcuts come in the form of file.desktop which is really a toml or ini file, so is easy to just change the Exec path to the annoying popup we want to show.

For windows I had to hook in to a windows module to be able to edit the shortcut, the one caveat with showing the original exe icon on the shortcut, is that you can right click and look at where the icon is pointing to. If you children doesn't have admin rights you will be Ok, but if they do have admin rights it will be another story as they can see the path to the random.exe which is the original file.

My children have Kubuntu and Windows 10, so I only did an initial test on a Mac VM I happened to have. It worked fine for binaries. The big issue about Mac is that if you go into applications, apps are bundled into a Application.app then if you do show contents, somewhere in there is the Mac_OS sh binary which launches that application. I couldn't figure out how to make a true shortcut. So on mac, you'll get the can't launch application when the binary is obsfuscated.

## When everything fails

If you think you've lost a binary, just run the `--recover` command. If that doesn't work look at the obs-paths.conf random path. As always when randomizing names, and file sizes things can get hard to recover, so make sure you have installer backups or at the very least backup binaries and shortcuts.
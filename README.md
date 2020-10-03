# App-Blocker An application to hide pesky games during school time

> NB: Backup binaries and shortcuts, as the app is going through beta and alpha testing. The app has good mechanisms so far to avoid overriding obsfuscated files, and recoving. Will add backup cli command to an external drive later on.

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

Ensure the child account doesn't have admin rights, or sudo access. Or else it can render this app useless by reinstalling software.

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

## Screenshots


## Extra Work to be aware of

There are some things to be aware of, some applications launch/spawn other processes in certain ocassions. One example of this is games or applications that use java. In this ocassions killing the main binary pid isn't enough, and you'll need to search what are the other processes that need to killed.

## OS Differences

Developing an application for multiple OSes is always a pain. The core of the application was pretty solid, but as I started adding features I was aware that I needed to separate items based on OS.

If you only use this for binaries, then all three major OSes, Linux, Windows, and Mac work about the same. When I say binaries it can be anything that can execute.

For the shortcut re-target modification is when things became more complicated for me at least on Debian/Ubuntu shortcuts come in the form of file.desktop which is really a toml or ini file, so is easy to just change the Exec path to the annoying popup we want to show.

For windows I had to hook in to a windows module to be able to edit the shortcut, the one caveat with showing the original exe icon on the shortcut, is that you can right click and look at where the icon is pointing to. If you children doesn't have admin rights you will be Ok, but if they do have admin rights it will be another story as they can see the path to the random.exe which is the original file.

My children have Kubuntu and Windows 10, so I only did an initial test on a Mac VM I happened to have. It worked fine for binaries. The big issue about Mac is that if you go into applications, apps are bundled into a Application.app then if you do show contents, somewhere in there is the Mac_OS sh binary which launches that application. I couldn't figure out how to make a true shortcut. So on mac, you'll get the can't launch application when the binary is obsfuscated.

## When everything fails

If you think you've lost a binary, just run the `--recover` command. If that doesn't work look at the obs-paths.conf random path. As always when randomizing names, and file sizes things can get hard to recover, so make sure you have installer backups or at the very least backup binaries and shortcuts.
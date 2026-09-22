# REPL / running
mpremote (opens REPL)
mpremote connect <dev> (connect to device)
mpremote disconnect (disconnect)
mpremote repl (enter REPL)
mpremote eval <expr> (evaluate/print expr)
mpremote exec <code> (execute python code)
mpremote run <file> (run local script)
    mpremote run <file> --no-follow (returns immediately and leaves the device running the script in the background)

# Filesystem
mpremote fs ls (list files)
mpremote fs cp <src> <dest> (copy files) (: in front for remote file)
    example: `mpremote fs cp lib/BMP280.py :lib/BMP280.py`
mpremote fs rm <file> (remove file)
mpremote fs mkdir <dir> (create directory)
mpremote fs rmdir <dir> (remove directory)
mpremote fs cat <file> (display file content)

# misc
mpremote mount <dir> (mount local folder)
mpremote soft-reset (soft reset)
mpremote bootloader (enter bootloader)
mpremote mip install <pkg> (install package) 
mpremote devs (list connected devices)
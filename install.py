import os
from os.path import expanduser
import glob
import shutil
from pathlib import Path
import urllib.request
import zipfile
import sys
from threading import Thread
from queue import Queue

holodeck_binary_website = "http://pcc.byu.edu/holodeck/"
holodeck_binary_name = "DefaultWorlds_1.02.zip"
block_size = 1000000  # 1mb


def expand_tilde(in_text):
    if in_text[0] == "~":
        home_directory = expanduser("~")
        in_text = in_text.replace("~", home_directory, 1) + in_text[1:]
    return in_text


def _setup_binary(binary_location, worlds_path):
    def file_writer_worker(path, length, q):
        amount_written = 0
        with open(file_loc, 'wb') as f:
            while amount_written < length:
                f.write(q.get())
                amount_written += block_size
                percent_done = 100 * amount_written / length
                sys.stdout.write("\r%d%%" % int(percent_done))
                sys.stdout.flush()

    # Download the binary
    print("Downloading default worlds...")
    q = Queue()
    file_loc = os.path.join(worlds_path, holodeck_binary_name)
    with urllib.request.urlopen(binary_location) as conn:
        length = int(conn.headers["Content-Length"])
        print("File length:", length)
        amount_read = 0
        write_thread = Thread(target=file_writer_worker, args=(file_loc, length, q))
        write_thread.start()
        while amount_read < length:
            q.put(conn.read(block_size))
            amount_read += block_size
        write_thread.join()
        print()

    # Unzip the binary
    print("Unpacking worlds...")
    with zipfile.ZipFile(file_loc, 'r') as zip_file:
        zip_file.extractall(worlds_path)
    os.remove(file_loc)


def linux_installation():
    default_path = "/usr/local"

    print("Beginning Linux installation")
    path = input("Please choose installation path (Default is /usr/local): ")
    if path == "":
        path = default_path

    path = expand_tilde(path)

    if not os.path.isdir(path):
        print("Unable to find path: " + path)
        return

    try:
        base_path = os.path.join(path, "Holodeck")
        worlds_path = os.path.join(base_path, "worlds")
        holodeck_path = os.path.join(base_path, "Holodeck")
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        if not os.path.exists(worlds_path):
            os.mkdir(worlds_path)
        if not os.path.exists(holodeck_path):
            os.mkdir(holodeck_path)
        print("Installing at:", os.path.join(path, "Holodeck"))

        for file in glob.glob("Holodeck/*.py"):
            shutil.copyfile(file, os.path.join(path, "Holodeck", "Holodeck", file.split("/")[-1]))

        os.chmod(worlds_path, 0o755)
        _setup_binary(holodeck_binary_website + "Linux_" + holodeck_binary_name, worlds_path)

        # Make the binary executable
        for path, _, _ in os.walk(os.path.join(worlds_path, "LinuxDefaultWorlds")):
            os.chmod(path, 0o777)
        binary_path = os.path.join(worlds_path, "LinuxDefaultWorlds/LinuxNoEditor/Holodeck/Binaries/Linux/Holodeck")
        os.chmod(binary_path, 0o755)

        print("To continue installation, follow instructions on the github page")
        print("https://github.com/byu-pccl/HolodeckPythonBinding")
        print("Ensure to add the installed directory to your Python path")

    except PermissionError:
        print("Insufficient permissions, cannot install at specified path. Try with sudo")


def windows_installation():
    default_path = os.path.join(str(Path.home()), "AppData", "Local")

    print("Beginning Windows installation")
    path = input("Please choose installation path (Default is C:\\User\\user_name\\AppData\\Local): ")
    if path == "":
        path = default_path

    path = expand_tilde(path)

    if not os.path.isdir(path):
        print("Unable to find path: " + path)
        return

    try:
        base_path = os.path.join(path, "Holodeck")
        worlds_path = os.path.join(base_path, "worlds")
        holodeck_path = os.path.join(base_path, "Holodeck")
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        if not os.path.exists(worlds_path):
            os.mkdir(worlds_path)
        if not os.path.exists(holodeck_path):
            os.mkdir(holodeck_path)
        print("Installing at:", os.path.join(path, "Holodeck"))

        for file in glob.glob("Holodeck\\*.py"):
            shutil.copyfile(file, os.path.join(path, "Holodeck", "Holodeck", file.split("\\")[-1]))

        _setup_binary(holodeck_binary_website + "Windows_" + holodeck_binary_name, worlds_path)

        print("To continue installation, follow instructions on the github page")
        print("https://github.com/byu-pccl/HolodeckPythonBinding")
        print("Ensure to add the installed directory to your path")

    except PermissionError:
        print("Insufficient permissions, cannot install at specified path.")


if os.name == "posix":
    linux_installation()
elif os.name == "nt":
    windows_installation()
else:
    raise NotImplementedError("Holodeck is only supported for Linux and Windows")

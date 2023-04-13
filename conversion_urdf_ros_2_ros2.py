import os
import shutil
import sys

# Configuration variable

# This variable is the path to the solidworks output folder containing the urdf files
source_dir = '../solidworks_export/'

# This variable is the name for the ROS 2 package
package_name = "system_x_description"

# This variable is the path for the ROS 2 package
package_directory = '../'
target_dir = package_directory + package_name + '/'

# This variable is the name of the URDF file that SolidWorks outputs
source_urdf_file_name = "7mm_Concept_Group.SLDASM"

# This variable defines the name of the target URDF in the ROS 2 package
target_urdf_file_name = "robot"

# Maintainer, description, license and version that will be added to the package xml and setup.py
maintainer_name = "Marc Bestmann"
maintainer_mail = "marc.bestmann@dlr.de"
description = "Description package for the System-X robot"
license_type = "TODO"
version_number = "0.0.1"


def run_command_dir(command_dir, command):
    os.system("cd " + command_dir + " && " + command)


def replace_str(file, old_str, new_str):
    file_data = ""
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line
    with open(file, "w", encoding="utf-8") as f:
        f.write(file_data)


if __name__ == '__main__':
    # Check if this is a new package or if we might override something
    if os.path.exists(target_dir) and (os.listdir(target_dir) != 0):
        sys.stdout.write(
            f"Target directory {target_dir} is not empty. Previous files might be deleted to create the ROS2 package. Continue? [Y/n]")
        choice = input().lower()
        if choice not in ["y", ""]:
            exit()
    if not os.path.exists(target_dir):
        # create the directory of the package
        run_command_dir(package_directory, f"mkdir {package_name}")
    # Remove old folders to ensure that we don't keep old files from previous version (i.e. meshes with different names)
    folders = ["launch", "meshes", "meshes/collision",
               "meshes/visual", "urdf", "rviz", "resource"]
    for folder in folders:
        if os.path.exists(f"{target_dir}/{folder}"):
            run_command_dir(target_dir, f"rm -r {folder}")
    # Create new empty folders
    for folder in folders:
        run_command_dir(target_dir, f"mkdir {folder}")

    # Copy files
    # Copy stl files
    run_command_dir(source_dir, "cp -r ./meshes/* " +
                    target_dir + "meshes/visual")
    run_command_dir(source_dir, "cp -r ./meshes/* " +
                    target_dir + "meshes/collision")
    # Copy urdf files
    run_command_dir(source_dir, "cp  ./urdf/" +
                    source_urdf_file_name + ".urdf " + target_dir + "urdf/")
    # rename URDF
    run_command_dir(target_dir, "mv ./urdf/" +
                    source_urdf_file_name + ".urdf " + target_dir + "urdf/" + target_urdf_file_name + ".urdf")
    # create empty file to install marker in the package index
    run_command_dir(target_dir, f"touch ./resource/{package_name}")

    # replace file
    os.system("cp -f ./replace_files/setup.py " + target_dir)
    os.system("cp -f ./replace_files/setup.cfg " + target_dir)
    os.system("cp -f ./replace_files/package.xml " + target_dir)
    os.system("cp -f ./replace_files/launch.py " + target_dir + "launch")
    os.system("cp -f ./replace_files/default.rviz " + target_dir + "rviz")

    # Change file content
    # launch.py
    replace_str(target_dir + "launch/launch.py", "PACKAGE_NAME", package_name)
    replace_str(target_dir + "launch/launch.py",
                "URDF_NAME.urdf", target_urdf_file_name + ".urdf")
    # setup.py
    replace_str(target_dir + "setup.py", "PACKAGE_NAME", package_name)
    replace_str(target_dir + "setup.cfg", "PACKAGE_NAME", package_name)
    # package.xml
    replace_str(target_dir + "package.xml", "PACKAGE_NAME", package_name)
    replace_str(target_dir + "package.xml", "MAINTAINER_NAME", maintainer_name)
    replace_str(target_dir + "package.xml", "MAINTAINER_MAIL", maintainer_mail)
    replace_str(target_dir + "package.xml", "LICENSE_TYPE", license_type)
    replace_str(target_dir + "package.xml", "VERSION_NUMBER", version_number)
    replace_str(target_dir + "package.xml", "DESCRIPTION_TEXT", description)
    # urdf files
    replace_str(target_dir + "urdf/" + target_urdf_file_name + ".urdf", source_urdf_file_name + "/meshes",
                package_name + "/meshes/visual")
    replace_str(target_dir + "urdf/" + target_urdf_file_name + ".urdf", source_urdf_file_name,
                target_urdf_file_name)

    # Insert base_footprint
    keyword = "name=\"" + target_urdf_file_name + "\">"
    str = ""
    with open("./replace_files/insert_content.txt", "r", encoding="utf-8") as f:
        str = f.read()
    file = open(target_dir + "/urdf/" + target_urdf_file_name + ".urdf", 'r')
    content = file.read()
    post = content.find(keyword)
    if post != -1:
        content = content[:post + len(keyword)] + \
            "\n" + str + content[post + len(keyword):]
        file = open(target_dir + "/urdf/" +
                    target_urdf_file_name + ".urdf", "w")
        file.write(content)
    file.close()

    print("conversion success!")

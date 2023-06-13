import os
import shutil
import sys
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
import argparse


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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir", help="The path to the solidworks output folder containing the urdf files", type=str)
    parser.add_argument("--package-name",
                        help="The name for the ROS 2 package", type=str)
    parser.add_argument("--package-directory",
                        help="The path for the ROS 2 package", type=str)
    parser.add_argument("--source-urdf-file-name",
                        help="The name of the URDF file that SolidWorks outputs", type=str)
    parser.add_argument("--target-urdf-file-name",
                        help="Defines the name of the target URDF in the ROS 2 package", type=str)
    parser.add_argument("--maintainer-name",
                        help="Will be added to the package xml and setup.py", type=str)
    parser.add_argument("--maintainer-mail",
                        help="Will be added to the package xml and setup.py",  type=str)
    parser.add_argument(
        "--description", help="Will be added to the package xml and setup.py",  type=str)
    parser.add_argument(
        "--license_type", help="Will be added to the package xml and setup.py",  type=str)
    parser.add_argument(
        "--version_number", help="Will be added to the package xml and setup.py", type=str)
    args = parser.parse_args()
    source_dir = args.source_dir
    package_name = args.package_name
    package_directory = args.package_directory
    target_dir = package_directory + package_name + '/'
    source_urdf_file_name = args.source_urdf_file_name
    target_urdf_file_name = args.target_urdf_file_name
    maintainer_name = args.maintainer_name
    maintainer_mail = args.maintainer_mail
    description = args.description
    license_type = args.license_type
    version_number = args.version_number

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
                    source_urdf_file_name + ".urdf " + "./urdf/" + target_urdf_file_name + ".xacro")
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
    replace_str(target_dir + "urdf/" + target_urdf_file_name + ".xacro", source_urdf_file_name + "/meshes",
                package_name + "/meshes/visual")
    replace_str(target_dir + "urdf/" + target_urdf_file_name + ".xacro", source_urdf_file_name,
                target_urdf_file_name)

    # remove fake link collisions and visuals that are wrongly exported from solidworks
    replace_str(target_dir + "urdf/" + target_urdf_file_name + ".xacro", source_urdf_file_name + "/meshes",
                package_name + "/meshes/visual")

    # Insert base_footprint
    keyword = "name=\"" + target_urdf_file_name + "\">"
    str = ""
    with open("./replace_files/insert_content.txt", "r", encoding="utf-8") as f:
        str = f.read()
    file = open(target_dir + "/urdf/" +
                target_urdf_file_name + ".xacro", 'r')
    content = file.read()
    post = content.find(keyword)
    if post != -1:
        # add xacro note and insert_content.txt
        content = content[:post] + "xmlns:xacro=\"http://www.ros.org/wiki/xacro\"\n  " + keyword + \
            "\n" + str + content[post + len(keyword):]
        file = open(target_dir + "/urdf/" +
                    target_urdf_file_name + ".xacro", "w")
        file.write(content)
    file.close()

    # remove non existing link visuals and collision files
    stl_path = source_dir + "/meshes/"
    stl_files = [f for f in listdir(stl_path) if isfile(join(stl_path, f))]
    ET.register_namespace('xacro', "http://www.ros.org/wiki/xacro")
    tree = ET.parse(target_dir + "/urdf/" + target_urdf_file_name + ".xacro",
                    ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    root = tree.getroot()
    # we want to keep those links who have an existing mesh file
    links_to_keep = []
    for stl_file in stl_files:
        links_to_keep = links_to_keep + \
            root.findall(".//mesh[@filename='package://" + package_name +
                         "/meshes/visual/" + stl_file + "']/../../..")
    # get all links to find out for which we need to delete the meshes
    links = root.findall(".//mesh/../../..")
    links_to_delete = set(links) - set(links_to_keep)
    for link in links_to_delete:
        elements = link.findall(".//mesh/../..")
        for element in elements:
            link.remove(element)

    # correct the path to the stl for collision files
    collision_meshes = root.findall(".//collision/geometry/mesh")
    for collision_mesh in collision_meshes:
        old_path = collision_mesh.get('filename')
        new_path = old_path.replace('visual', 'collision')
        collision_mesh.set('filename', new_path)

    # save modified URDF
    tree.write(target_dir + "urdf/" + target_urdf_file_name + ".xacro")
    print("conversion success!")

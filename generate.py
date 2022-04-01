# Written by Coolsonickirby/Random
# Music of the day: BlazBlue CPEX Opening (https://www.youtube.com/watch?v=-oKoi8JkvCE)

import os, subprocess, json
import shutil
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

def loadMSBT(path):
    out = "tmp.json"
    subprocess.call(["dotnet", "MSBTEditorCli.dll", path, out])
    data = []
    with open(out, encoding='utf-8') as f:
        data = json.load(f)
    os.remove(out)
    return data

def makeDirs(path):
    try:
        os.makedirs(path, 777, exist_ok=True)
    except:
        pass


msbts_og_data = {}
modded_msbts = []
msbts = {}

if __name__ == "__main__":
    src = input("Enter mods path: ")
    while os.path.exists(src) == False:
        print("Path does not exist. Please enter a path that does exist")
        src = input("Enter mods path: ")

    del_ogs = input("Would you like to delete the original msbt files (will copy them to a backup folder)? (y/n) ")
    while del_ogs.lower() not in ["y", "n"]:
        print("Invalid choice.")
        del_ogs = input("Would you like to move the detected msbt files to a backups folder (will remove them from mod folders)? (y/n) ")

    del_ogs = del_ogs == "y"

    print("Loading original msbts....")

    for x in os.listdir("./msbts"):
        if x.endswith(".msbt") == False:
            continue
        print("Loading %s....." % x)
        msbtName = os.path.splitext(x)[0]
        msbts_og_data[msbtName] = []
        msbts_og_data[msbtName] = {y["label"]:y["value"] for y in loadMSBT("./msbts/%s" % x)["strings"]}

    print("Scanning for msbts in mods path....")    
    for root, dirs, files in os.walk(src):
        for filename in files:
            full_path = os.path.join(root, filename)
            name, ext = os.path.splitext(filename)
            if ext != ".msbt":
                continue

            if name not in msbts_og_data:
                print("Found %s but name does not match any original msbt file. Ignoring." % full_path)
            else:
                print("Found %s!" % full_path)
                modded_msbts.append(full_path)

    if len(modded_msbts) <= 0:
        print("No MSBT file detected in mod path!")

    for x in modded_msbts:
        print("Generating XMSBT for %s...." % x)
        name, ext = os.path.splitext(os.path.basename(x))
        lbls_xmsbt = {}
        data = loadMSBT(x)["strings"]
        for entry in data:
            if entry["label"] not in msbts_og_data[name] or entry["value"] != msbts_og_data[name][entry["label"]]:
                lbls_xmsbt[entry["label"]] = entry["value"]
        xmsbt_root = Element("xmsbt")
        for lbl in lbls_xmsbt:
            xmsbtLBL = SubElement(xmsbt_root, "entry", {"label": "%s" % lbl})
            value = SubElement(xmsbtLBL, "text")
            value.text = lbls_xmsbt[lbl]
        try:
            xmsbt_string = minidom.parseString(tostring(xmsbt_root, encoding='utf-16', method='xml').decode('utf-16')).toprettyxml(indent="   ")
        except:
            xmsbt_string = tostring(xmsbt_root, encoding='utf-16', method='xml').decode('utf-16')
        with open("%s/%s.xmsbt" % (os.path.dirname(x), name), "w", encoding='utf-16') as handle:
            handle.write(xmsbt_string)
        print("Generated %s XMSBT!" % x)
        if del_ogs:
            modPath = os.path.splitext(x[len(src):])[0]
            backupPath = "./backups/%s" % modPath
            makeDirs(backupPath)
            shutil.move(x, backupPath)
            
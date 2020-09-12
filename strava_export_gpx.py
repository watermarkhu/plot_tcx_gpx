#!/usr/bin/python3
import os
import re
import subprocess
import csv
import sys

# CONSTANTS ------------------------------------

# ----------------------------------------------

# unzip and delete the archive -----------------


def unzip(file):
    import gzip
    import shutil
    with gzip.open(file, 'rb') as f_in:
        with open(file.lower().replace('.gz', ''), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(file)

# helper for executing babel -------------------


def exec_cmd(command):
    result = subprocess.Popen(command, shell=True)
    text = result.communicate()[0]
    return_code = result.returncode
    if return_code != 0:
        return False
    return True

# exit with error ------------------------------


def die(error):
    print("Error: " + error)
    quit()

# main -----------------------------------------


def main(UNZIPPED_FOLDER, STRAVA_ACTIVITIES_SUBFOLDER, STRAVA_ACTIVITIES_FILE):

    # assemble paths
    strava_unzipped_folder = os.path.join(".", UNZIPPED_FOLDER)
    strava_unzipped_activities_folder = os.path.join(".", UNZIPPED_FOLDER, STRAVA_ACTIVITIES_SUBFOLDER)
    strava_unzipped_activities_file = os.path.join(".", UNZIPPED_FOLDER, STRAVA_ACTIVITIES_FILE)

    # gpsbabel command, expecting to be in PATH. You may put the absolute path to the executable (mostly for Windows users)
    gpsbabel_command = "gpsbabel -w -t -i gtrnctr -f {filename_tcx} -o gpx,gpxver=1.1 -F {filename_gpx} > /dev/null"

    # pre-check
    if not os.path.exists(strava_unzipped_folder):
        die("Folder with expected unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_folder))

    if not os.path.exists(strava_unzipped_activities_folder):
        die("Folder with activities in unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_activities_folder))

    if not os.path.isfile(strava_unzipped_activities_file):
        die("File with activities in unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_activities_file))

    # reading the activities.csv file and storing the list in activities_list
    print("Reading '{path}'".format(path=strava_unzipped_activities_file))
    try:
        with open(strava_unzipped_activities_file, newline='\n', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            activities_list = list(reader)
    except Exception as ex:
        die("Cannot read '{path}'. {err}".format(path=strava_unzipped_activities_file, err=str(ex)))

    # get the count of the activities
    cnt = len(activities_list)
    print("Found {cnt} activities ".format(cnt=str(cnt)))

    # let's go through the list and unzip any .gz files if exists
    print("Unzipping ...")
    sys.stdout.write("Progress: ")
    ucnt = 0
    for line in activities_list:
        x = 0
        filename = os.path.join(strava_unzipped_folder, line['Filename'])
        ucnt += 1
        # sys.stdout.write("{:2.0%}".format(ucnt / cnt).rjust(5, " "))
        # sys.stdout.flush()
        if filename.endswith(".gz") and os.path.exists(filename):
            unzip(filename)
        line['Filename'] = line['Filename'].replace(".gz", "")
        # sys.stdout.write("\b\b\b\b\b")
        # sys.stdout.flush()
        x += 1
    sys.stdout.write("\n")

    # now remove extra \n from GPX and convert TCX to GPX using gpsbabel
    print("Normalizing ...")

    activities_type = dict()
    for line in activities_list:
        filename = os.path.join(strava_unzipped_folder, line['Filename'])
        extension = os.path.splitext(filename)[1][1:].strip().lower()


        # if os.path.exists(filename):
        if extension == "gpx":
            if os.path.exists(filename):
                with open(filename, encoding='utf-8') as file:
                    content = file.read()
                    fixed = re.sub(r'>\s\s+<', '><', content).strip()
                    with open(filename, "w", encoding='utf-8') as filew:
                        filew.write(fixed)

        # strip spaces from tcx
        if extension == "tcx":
            line['Filename'] = line['Filename'].replace(".tcx", ".gpx")
            if os.path.exists(filename):
                with open(filename, encoding='utf-8') as file:
                    content = file.read()
                    fixed = re.sub(r'>\s\s+<', '><', content).strip()
                    with open(filename, "w", encoding='utf-8') as filew:
                        filew.write(fixed)
                        print(re.findall(r'<[Aa][Cc][Tt][Ii][Vv][Ii][Tt][Yy][ ]{1,}[Ss][Pp][Oo][Rr][Tt]="([^"]*)">', fixed))

                    filename_gpx = filename.replace(".tcx", ".gpx")
                    rc = exec_cmd(gpsbabel_command.format(
                        filename_gpx=filename_gpx,
                        filename_tcx=filename)
                    )
                    if not rc:
                        print('error')
                    else:
                        os.remove(filename)
        
        print(line['Filename'].ljust(40, " ") + "| " + line["Activity Type"].ljust(13, " ") + "| " + str(line["Activity Name"])[:70])
        activities_type[line['Filename']] = line["Activity Type"]
        


    return activities_type
# run ------------------------------------------------------
if __name__ == "__main__":
    UNZIPPED_FOLDER = "/mnt/d/Users/water_000/Downloads/export_25412727/"
    STRAVA_ACTIVITIES_SUBFOLDER = "/mnt/d/Users/water_000/Downloads/export_25412727/activities"
    STRAVA_ACTIVITIES_FILE = "/mnt/d/Users/water_000/Downloads/export_25412727/activities.csv"
    main(UNZIPPED_FOLDER, STRAVA_ACTIVITIES_SUBFOLDER, STRAVA_ACTIVITIES_FILE)

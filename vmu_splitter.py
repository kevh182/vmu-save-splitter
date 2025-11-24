from vmu.vmu import Vmu;
from vmu.vmu_file import VmuFile;
from file_log import FileLog
from dbs.save_db import SaveDb;
from dbs.game_db import GameDb;
import configparser
import fnmatch
from pathlib import Path
import shutil

config = configparser.ConfigParser()

try:
     with open('./cfg.ini') as f:
          config.read_file(f)
except IOError:
     raise Exception("cfg.ini missing")

import_dir = "./import/"
export_dir = "./export/"

if (not "Options" in config):
     raise Exception("cfg.ini invalid")

if (not "loader" in config["Options"]):
     raise Exception("'loader' option missing from config.")

empty = True if ("empty" in config["Options"] and config["Options"]["empty"] == "1") else False

regions = config["Options"]["region"].split(",") if "region" in config["Options"] else []
loader = config["Options"]["loader"]

first_generic_number = int(config["Options"]["first_generic_number"]) if ("first_generic_number" in config["Options"] and config["Options"]["first_generic_number"]).isdigit() else None

save_db = SaveDb()
game_db = GameDb()
file_log = FileLog()

def empty_export_folder():
    export_folder = Path(export_dir)
    if(export_folder.is_dir()):
        shutil.rmtree(export_dir)
        
    Path(export_dir).mkdir()
    with open(f'{export_dir}/generated vmu files will appear here', 'w') as fp:
        pass


def sort_func(e):
    if (e['region'] == "USA"):
        return "1"
    if (e['region'] == "Japan"):
        return "2"
    if (e['region'] == "Europe"):
        return "3"
    else:
        return e['region']
    
def user_yes_no(query: str, **kwargs):
    default_yes = kwargs.get("default_yes", False)
    options = "(Y/n)" if default_yes else "(y/N)"

    while 1:
        response = input(f'{query} {options}:\n')
        if (response == ""):
            return True if default_yes else False
        
        if (response.lower() == "y" or response.lower() == "yes"):
            return True
        
        if (response.lower() == "n" or response.lower() == "no"):
            return False
        
        print("Invalid input")

def match_game(matches, file_name):
    matched_game = None
    if(loader == "disc"):
        fmids = []
        for match in matches:
              fmids.append(match["fmid"])
        if(len(set(fmids)) == 1):
             return matches[0]
        
    matched_games = []

    for region in regions:
        if (len(matched_games) == 0):
            for match in matches:
                if match["region"] == region:
                    matched_games.append(match)

    if (len(matched_games) == 1):
        return matched_games[0]
    elif (len(matched_games) > 1):
        matches = matched_games
    
    matches.sort(key=sort_func)
            
    print(f"\n{len(matches)} matches for {file_name}:")
    for index, match in enumerate(matches):
            title = match["title"]
            region = match["region"]
            print(f"   [{index + 1}] {title} ({region})")

    selection = input("Select the matching game from the list above (Leave blank to skip):\n")
    if selection and matches[int(selection)-1]:
        match = matches[int(selection)-1]
        matched_game = match
    else:
        print("Skipping...\n")

    return matched_game


# Converts GameIDs for openMenu, based on information from the openMenu source code
# located at https://github.com/megavolt85/openmenu
def open_menu_serials(matched_game):
    formatted_game_id = format_game_id(matched_game["game_id"])
    # Fix Alone in the Dark (PAL) overlapping Alone in the Dark (USA)
    if(formatted_game_id == "T15117N" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "T15112D05"
        return matched_game
    
    # Fix Crazy Taxi (PAL) overlapping Crazy Taxi (USA)
    if(formatted_game_id == "MK51035" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "MK5103550"
        return matched_game
    
    # Fix Disney's Donald Duck: Goin' Quackers (USA) overlapping
    # Disney's Donald Duck: Quack Attack (PAL)
    if(formatted_game_id == "T17714D50" and matched_game["region"] == "USA"):
        matched_game["game_id"] = "T17719N"
        return matched_game
    
    # Fix Floigan Bros (PAL) overlapping Floigan Bros (USA)
    if(formatted_game_id == "MK51114" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "MK5111450"
        return matched_game
    
    # Fix Legacy of Kain: Soul Reaver (PAL) overlapping
    # Legacy of Kain: Soul Reaver (USA)
    if(formatted_game_id == "T36802N" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "T36803D05"
        return matched_game
    
    # Fix NBA2K2 (PAL) overlapping NBA2K2 (USA)
    if(formatted_game_id == "MK51178" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "MK5117850"
        return matched_game
    
    # Fix NBA Showtime (PAL) overlapping 4 Wheel Thunder (PAL)
    if(formatted_game_id == "T9706D50" and matched_game["title"] == "NBA Showtime: NBA on NBC"):
        matched_game["game_id"] = "T9705D50"
        return matched_game
    
    # Fix Nightmare Creatures II (USA) overlapping Dancing Blade 2 (JAP)
    if(formatted_game_id == "T9504M" and matched_game["region"] == "USA"):
        matched_game["game_id"] = "T9504N"
        return matched_game
    
    # Fix Plasma Sword (PAL) overlapping Street Fighter Alpha 3 (PAL)
    if(formatted_game_id == "T7005D50" and matched_game["title"] == "Plasma Sword: Nightmare of Bilstein"):
        matched_game["game_id"] = "T7003D"
        return matched_game
    
    # Fix Skies of Arcadia (PAL) overlapping Skies of Arcadia (USA)
    if(formatted_game_id == "MK51052" and matched_game["region"] == "Europe"):
        matched_game["game_id"] = "MK5105250"
        return matched_game
    
    # Fix Spider-Man (PAL) overlapping Spider-Man (USA)
    if(formatted_game_id == "T13008N" and matched_game["region"] != "USA"):
        matched_game["game_id"] = "T13011D50"
        return matched_game
    
    # Fix TNN Motorsports (USA) overlapping Metal Slug 6 (AW)
    if(formatted_game_id == "T0000M" and matched_game["title"] == "TNN Motorsports Hardcore Heat"):
        matched_game["game_id"] = "T13701N"
        return matched_game
    
    # Fix Maximum Speed (AW) overlapping Dolphin Blue (AW)
    if(formatted_game_id == "T0006M" and matched_game["title"] == "Maximum Speed"):
        matched_game["game_id"] = "T0010M"
        return matched_game
    
    # Fix Fist of North Star (AW) overlapping Rumble Fish (AW)
    if(formatted_game_id == "T0009M" and matched_game["title"] == "Fist of the North Star"):
        matched_game["game_id"] = "T0026M"
        return matched_game

    return matched_game

def format_game_id(game_id: str):
    # if (loader == "openMenu"):
    #     if(game_id.find(" ") > -1):
    #         return game_id[:game_id.find(" ")].replace("-","").replace(" ", "").strip()
    # if (loader == "MODE"):
    #     if(game_id.rfind(" ") > -1):
    #         return game_id[:game_id.rfind(" ")].replace("-","").replace(" ", "").strip()
        
    return game_id.replace("-","").replace(" ", "").strip()

def save_to_generic_vmu(file: VmuFile):
    current_card_num = first_generic_number
    saved = False

    while(not saved):
        file_dir = f"{export_dir}MemoryCard{current_card_num}"
        if(not Path(file_dir).is_dir()):
             Path(file_dir).mkdir()

        file_path = f"{file_dir}/MemoryCard{current_card_num}-1.vmu"
        is_file = Path(file_path).is_file()
        vmu = Vmu(file_path) if is_file else Vmu("./blank.vmu")

        try:
            vmu.add_file(file)
            vmu.save_vmu(file_path)
            saved = True
        except Exception as e:
            msg = getattr(e, 'message', str(e))
            if(msg == "Not enough space on VMU" or msg == "File already exists"):
                current_card_num += 1
            else:
                print(e)
                return

def split_files(vmu: Vmu):
    new_vmus = {}
    matched_ids = []
    for file in vmu.directory.files():
        if (file.file_name == "ICONDATA_VMS"):
             continue
        matches = []
        for index,save_name in enumerate(save_db.save_names):
            if fnmatch.fnmatch(file.file_name, save_name):
                matches.append(save_db.save_data[index])
            
        matched_game = None
        if(len(matches) == 0):
            print(f"No matches for {file.file_name}")
            if(loader != "disc"):
                current_file = vmu.get_file(file.index)
                result = find_game(file.file_name, current_file)
                if(result):
                    matched_game = {
                        "title": result["title"],
                        "game_id": result["game_id"],
                        "region": result["region"],
                        "fmid": ""
                    }

        elif(len(matches) == 1):
            matched_game = matches[0]
        else:
            for match in matches:
                 if(match["game_id"] in matched_ids):
                      matched_game = match
            matched_game = matched_game if matched_game else match_game(matches, file.file_name)

        if (matched_game):
            if (loader == "openMenu"):
                matched_game = open_menu_serials(matched_game)
            matched_ids.append(matched_game["game_id"])
            game_id = matched_game["fmid"] if loader == "disc" else format_game_id(matched_game["game_id"])
            print(f'Matched {matched_game["title"]} ({matched_game["region"]}): {game_id}')
            current_file = vmu.get_file(file.index)
            new_vmu: Vmu = new_vmus[game_id] if game_id in new_vmus else Vmu("./blank.vmu")

            new_vmu.add_file(current_file)
            new_vmus[game_id] = new_vmu
        elif (first_generic_number != None and first_generic_number > 0):
            save_to_generic = user_yes_no("Save to generic memory card?")
            if(save_to_generic):
                current_file = vmu.get_file(file.index)
                save_to_generic_vmu(current_file)
    
    for game_id, new_vmu in new_vmus.items():
        game_dir = Path(export_dir + game_id)
        if(not game_dir.is_dir()):
             game_dir.mkdir()

        i = 1
        while i <= 8:
            file_path = f"{export_dir}{game_id}/{game_id}-{i}.vmu"
            if Path(file_path).is_file():
                i += 1
            else:
                new_vmu.save_vmu(file_path)
                break

def find_game(file_name: str, file: VmuFile):
    print(f"File Data:")
    print(f"{file_name}")
    if(file.is_valid):
        print(f"{file.desc}")
        print(f"{file.desc_long}")
    else:
        print(f"Unable to read file data")
    do_search = user_yes_no("Search for matching game?")
    if(do_search):
        try_again = True
        while (try_again == True):
            try_again = False

            search = input("Type a string to search for:\n")
            results = game_db.find_games(search)
            # results.sort(key=sort_func)
            print(f"\n{len(results)} matches for \"{search}\":")

            if(len(results) == 0):
                try_again = user_yes_no("Try again?", default_yes=True)
                continue

            for index, result in enumerate(results):
                title = result["title"]
                region = result["region"]
                game_id = result["game_id"]
                edition = result["edition"]
                print(f"   [{index + 1}] {title} ({region}) [{game_id.strip()}] Edition: {edition}")

            selection = input("Select the matching game from the list above (Leave blank to abort):\n")

            valid_response = int(selection) <= len(results) if selection else True
            if (not valid_response):
                print("Invalid response")

            if (selection == "" or not valid_response):
                try_again = user_yes_no("Try again?", default_yes=True)

            if selection and valid_response:
                result = results[int(selection)-1]
                chosen_game = result
                title = result["title"]
                region = result["region"]
                game_id = result["game_id"]
                edition = result["edition"]
                file_log.write_line(f"[{file_name}] matched to {title} ({region}) [{game_id}] Edition: {edition}")
                return chosen_game
    
    file_log.write_line(f"[{file_name}] - no match found")
    return None
           

if (empty):
    empty_export_folder()


vmuList = Path(import_dir).glob("**/*.[vVbB][mMiI][uUnNdD]")

for vmu in vmuList:
    currentVmu = Vmu(str(vmu))
    try:
        split_files(currentVmu)
    except KeyboardInterrupt:
        print("Aborted by user")
        break
    except:
        print(f"Error reading file {str(vmu)}")
#!/usr/bin/env python3

import re
from datetime import datetime
import os.path
import json
import argparse


Start_pattern = r"(\d+-\d+-\d+) (\d+:\d+) (?:begin|BEGIN) .*"
End_pattern = r"(\d+-\d+-\d+) (\d+:\d+) (?:SUCCESS END|SUC END) .*"

#filename_bck = "/opt/firebird/script/log/nnf_asutp_bck.log"
#filename_rst = "/opt/firebird/script/log/nnf_asutp_rest_rst_log.txt"

alias_file = "/opt/firebird/databases.conf"
old_alias_file = "/opt/firebird/aliases.conf"
db_filename = ""

#json_filename = "/tmp/asutp.json"
json_struct = {"current_date":"" , "start_bck":"", "end_bck":"", "start_rst":"", "end_rst":"", "size_db":0 } 




def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-db", "--db_name", dest="db_name", help="Firebird DB name")
    options = parser.parse_args()
    return options

def search_db_filename(in_string):
    in_string =  re.search("(?:\A" + db_filename +"=)(.*?fdb)", in_string)
    if in_string:
        return in_string.group(1)


def get_date(string_list, pattern):
    result = re.findall(pattern, string_list)
    return result


def parse_log_file(filename):
    with open (filename) as file:
        line = file.readlines()[-4:]

        if line[-1].find('END') != -1:
            end_string = line[-1]
            if line[-2].find('begin') or line[-2].find('BEGIN') != -1:
                start_string = line[-2]
            else:
                print(f'В логах не найдены шаблоны начала лога.\nФайл лога {filename} ')
                exit(2)

        else:
            end_string = line[-2]
            if line[-3].find('begin') or line[-2].find('BEGIN') != -1:
                start_string = line[-3]
            else:
                print(f'В логах не найдены шаблоны начала лога.\nФайл лога {filename} ')
                exit(2)

        start_date = get_date(start_string, Start_pattern)
        end_date = get_date(end_string, End_pattern)

        #print(f"start={start_date} end={end_date}")
        return start_date, end_date

def delete_space(in_string):
    return  re.sub(r"\s+", "", in_string, flags=re.UNICODE)


def get_db_fullpath(alias_file):
    with open(alias_file, 'r') as file_handler:
        for line in file_handler:
            data = delete_space(line)
            if search_db_filename(data):
                db_filename = search_db_filename(data)
                return db_filename

options = get_arguments()
db_name = options.db_name
if db_name == None:
    print("Не задано имя базы данных")
    exit(2)

db_filename = db_name
filename_bck = f"/opt/firebird/script/log/{db_filename}_bck.log"
filename_rst = f"/opt/firebird/script/log/{db_filename}_rest_rst_log.txt"
json_filename = f"/tmp/{db_name}.json"


#check filename_bck
if not(os.path.exists(filename_bck)):
    print("Не найден лог файл")
    exit(2)

#check alias firebird
if not(os.path.exists(alias_file)):
    alias_file = old_alias_file



#Get_current_time
now = datetime.now().strftime("%Y-%m-%d %H:%M")
json_struct['current_date'] = now

#Get size DB 
fullpath_db = get_db_fullpath(alias_file)
if fullpath_db:
    json_struct['size_db'] = os.path.getsize(fullpath_db)

#Get bck time
json_struct['start_bck'], json_struct['end_bck'] = parse_log_file(filename_bck)

#Get rst time
json_struct['start_rst'], json_struct['end_rst'] = parse_log_file(filename_rst)

#Save json
try:
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_struct, f, ensure_ascii=False, indent=4)

except:
    print("Ошибка записи файла")
    exit(2)

print("OK")
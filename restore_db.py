#!/usr/bin/env python3


# V.2 2021-11-08
# V.2.1 2021-11-09  shutdown db
# V.2.2 2021-11-11  + options rar delete, + change date format in log, + USER and PASSWORD for connect db without script 
# V.2.3 2021-11-15 change log format

#опции
#-p путь куда ресторим бд
#-f имя файлы с архивом rar БД если указана опция -nr тогда указываем fbk файл
#-nr если файл fbk надо указывать эту опцию
#-old если указан этот параметр то сохраняется old база
#-ndf не удалять fbk файл после восстановления
#-ndr не удалять rar файл после восстановления
#-u имя пользоывтеля для коннекта к БД
#-p пароль для коннекта в БД

import subprocess
#import os.path
import os
import re
import logging
import argparse
import datetime


day_of_week = "." + str(datetime.datetime.today().isoweekday())
#print(day_of_week)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", dest="path")
    parser.add_argument("-f", "--file", dest="filename")
    parser.add_argument("-u", "--username", dest="username")
    parser.add_argument("-pas", "--password", dest="password")
    parser.add_argument("-nr", "--norar", nargs="?", dest="norar", const="True")
    parser.add_argument("-old", "--storeolddb", nargs="?", dest="storeolddb", const="True")
    parser.add_argument("-ndf", "--nodeletefbk", nargs="?", dest="nodeletefbk", const="True")
    parser.add_argument("-ndr", "--nodeleterar", nargs="?", dest="nodeleterar", const="True")
    options = parser.parse_args()
    return options

def config_log(path_log):
    format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#    date_log_format = '%d-%m-%y %H:%M:%S'
    date_log_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, filename=path_log, filemode='a', format=format_log, datefmt=date_log_format )
    #logging.info('This is Debug')


def save_log(msg, echo = True):
    logging.info(msg)
    if echo == True:
        print(msg)

def get_fbk_filename(string):
    str1 = "Extracting\s{1,}/"
    match = re.findall(r"^" + str1 + ".*?([\w\W]+)(?=.fbk)", string, re.MULTILINE)
    if match == []:
        save_log("В архиве rar нет fbk файла")
        end_log()
        exit(2)
    return "/" + match[0] + ".fbk"


def unrar_file(rar_file, path_to):
    try:
        res =  subprocess.check_output(["rar", "e", "-y", rar_file, path_to], encoding='utf-8' )
        return res
    except:
        save_log("Ошибка с rar файлом")
        end_log()
        exit(2)


def shutdown_db(fdb_filename):
    try:
        if os.path.exists(fdb_filename):
            res =  subprocess.check_output(["/opt/firebird/bin/gfix", "localhost:" + fdb_filename, "-shut", "-force", "0", "-user", DB_USERNAME, "-pa", DB_PASSWORD ], encoding='utf-8' )
            return res
    except:
        save_log(f"Ошибка shutdown-а БД {fdb_filename}")
        end_log()
        #exit(2)


def rename_file_to_old(src_file, day_of_week=""):
    try:
        subprocess.check_output(["mv", "-f", src_file, src_file + ".old" + day_of_week], encoding='utf-8' )


    except:
        save_log("Ошибка переименования файла в old")
        end_log()
        

def restor_db(fbk_name, fdb_name, firebird_log):
    if STORE_OLD_FDB == False:
        if os.path.exists(fdb_name):
            os.remove(fdb_name)
    if os.path.exists(fdb_name):
        rename_file_to_old(fdb_name)
    if os.path.exists(firebird_log):
        rename_file_to_old(firebird_log, day_of_week)
        
    try:
        #print(subprocess.check_output(["gbak", "-c", "-g", "-v", "-se", "localhost:service_mgr", fbk_name, fdb_name, "-y", firebird_log ], encoding='utf-8' ))
        res =  subprocess.check_output(["/opt/firebird/bin/gbak", "-c", "-v", "-se", "localhost:service_mgr", fbk_name, fdb_name, "-y", firebird_log, "-USER", DB_USERNAME, "-PASSWORD", DB_PASSWORD ], encoding='utf-8')
        return res
    except subprocess.CalledProcessError as e:
        save_log("Ошибка в восстановлении базы")
        save_log(e)
        end_log()
        exit(2)


def restor_db_loc(fbk_name, fdb_name, firebird_log):
    if STORE_OLD_FDB == False:
        if os.path.exists(fdb_name):
            os.remove(fdb_name)
    if os.path.exists(fdb_name):
        rename_file_to_old(fdb_name)
    if os.path.exists(firebird_log):
        rename_file_to_old(firebird_log)
        
    try:
        #print(subprocess.check_output(["gbak", "-c", "-g", "-v", "-se", "localhost:service_mgr", fbk_name, fdb_name, "-y", firebird_log ], encoding='utf-8' ))
        res =  subprocess.check_output(["/opt/firebird/bin/gbak", "-c", "-v", fbk_name, fdb_name, "-y", firebird_log, "-USER", DB_USERNAME, "-PASSWORD", DB_PASSWORD ], encoding='utf-8')
        return res
    except subprocess.CalledProcessError as e:
        save_log("Ошибка в восстановлении базы")
        save_log(e)
        end_log()
        exit(2)



def get_filename(fbk_filename):
    try:
        file_name = fbk_filename.split('/')[-1].split('.')[0]
        return file_name
    except:
        save_log("Не удалось получить имя файла")
        end_log()
        exit(2)


def check_path(path):
    if not (os.path.isdir(path)):
        os.mkdir(path, 777) 


def delete_files(files):
    try:
        for file_name in files:
            os.remove(file_name)
    except:
        print("Failed delete file : " + file_name)


def end_log():
    save_log("############################", False)


#
options = get_arguments()
if options.path and options.filename and options.username and options.password :
    WORK_PATH = options.path
    RAR_FILE = options.filename
    DB_USERNAME = options.username
    DB_PASSWORD = options.password


    if options.norar:
        NORAR = options.norar
        fbk_filename = WORK_PATH + options.filename
    else:
        NORAR = False

    if options.storeolddb == "True":
        STORE_OLD_FDB = True
    else:
        STORE_OLD_FDB = False


    if options.nodeletefbk == "True":
        DELETE_FBK = False
    else:
        DELETE_FBK = True


    if options.nodeleterar == "True":
        DELETE_RAR = False
    else:
        DELETE_RAR = True




else:
    save_log("Не заданы обязательные параметры")
    end_log()
    exit(2)

LOG_PATH = WORK_PATH + "log/"
FP_RAR_FILE = WORK_PATH + RAR_FILE


#инициализируем лог
config_log(LOG_PATH + get_filename(FP_RAR_FILE) + "_rst.log")
save_log("Run script " + RAR_FILE, False)

if NORAR == False:

    save_log("start unrar " + RAR_FILE , False)
    result_unrar = unrar_file(FP_RAR_FILE, WORK_PATH)
    save_log("end unrar " + RAR_FILE , False)
    fbk_filename = get_fbk_filename(result_unrar)


fb_detail_log = LOG_PATH + get_filename(fbk_filename) + '_detail.log'
check_path(LOG_PATH)
fdb_filename = WORK_PATH + get_filename(fbk_filename) + '_rst.fdb'
shutdown_db(fdb_filename)
save_log("BEGIN RESTORE " + fbk_filename, False)
result_restore = restor_db(fbk_filename, fdb_filename, fb_detail_log)
save_log("SUC END RESTORE " + fbk_filename , False)
save_log("############################", False)

#удаляем rar
if DELETE_RAR == True:
    save_log("Delete rar: " + FP_RAR_FILE, False)
    delete_files([FP_RAR_FILE])


#удаляем fbk
if DELETE_FBK == True:
    save_log("Delete fbk: " + fbk_filename, False)
    delete_files([fbk_filename])

#print(result_restore)


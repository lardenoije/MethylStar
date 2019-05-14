#!/usr/bin/env python
__author__ = "Yadollah Shahryary Dizaji"
__title__ = "setup.py"
__description__ = "Setup file for Pipeline."
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "shahryary@gmail.com"

import os,fnmatch,sys
import traceback
import logging
from os import listdir
from os.path import isfile, join
import ConfigParser
import subprocess
import re
from distutils.util import strtobool


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[1;32m'
    NOTE = '\033[1;35m'
    WARNING = '\033[1;33m'
    UPDATE = '\033[0;36m'
    FAIL = '\033[91m'
    QUES = '\033[1;96m'
    RED = '\033[1;31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def mcolor(txt):
    # colorize just location or some path
    return bcolors.OKBLUE + str(txt) + bcolors.ENDC


def ycolor(txt):
    # colorize just location or some path
    return bcolors.WARNING + str(txt) + bcolors.ENDC


def gcolor(txt):
    return "\n"+bcolors.UPDATE + str(txt) + bcolors.ENDC


def rcolor(txt):
    return "\n"+bcolors.RED + str(txt) + bcolors.ENDC


def qucolor(txt):
    return bcolors.QUES + str(txt) + bcolors.ENDC

# =======================
# Configuartion file function

class GrumpyConfigParser(ConfigParser.ConfigParser):
  """Virtually identical to the original method, but delimit keys and values with '=' instead of ' = '"""
  def write(self, fp):
    if self._defaults:
      fp.write("[%s]\n" % DEFAULTSECT)
      for (key, value) in self._defaults.items():
        fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
      fp.write("\n")
    for section in self._sections:
      fp.write("[%s]\n" % section)
      for (key, value) in self._sections[section].items():
        if key == "__name__":
          continue
        if (value is not None) or (self._optcre == self.OPTCRE):
          # This is the important departure from ConfigParser for what you are looking for
          key = "=".join((key, str(value).replace('\n', '\n\t')))

        fp.write("%s\n" % (key))
      fp.write("\n")


def read_config(section, get_string):
    config = GrumpyConfigParser()
    config.optionxform = str
    config.read('config/pipeline.conf')
    val_str = config.get(section, get_string)
    return val_str


def replace_config(section, old_string, new_string):

    config = GrumpyConfigParser()
    config.optionxform = str
    config.read('config/pipeline.conf')
    config.set(section, old_string, new_string)
    with open('config/pipeline.conf', 'wb') as config_file:
        config.write(config_file)

# =======================
# Pattern and files function


def find_file_pattern(path, pattern):

    list_files = list()
    for (dirpath, dirnames, filenames) in os.walk(path):
        list_files += [os.path.join(dirpath, file) for file in filenames]

    # Print the files
    list_dataset = []
    for elem in list_files:
        if fnmatch.fnmatch(elem, pattern):
            list_dataset.append(elem)
    return list_dataset


def check_empty_dir(path, pattern):
    try:
        files = list(find_file_pattern(read_config("GENERAL", "result_pipeline")+"/"+path, pattern))
        if files:
            for item in find_file_pattern(read_config("GENERAL", "result_pipeline")+"/"+path, pattern):
                files.append(item)
        else:
            files = []
        return files

    except Exception as e:
        logging.error(traceback.format_exc())
        message(2, "something is going wrong... please run again. ")
        print(e.message, e.args)


def true_false_fields_config(read_config_str, negated_bool):
    val_true_false = "unset"
    try:
        if str(bool(strtobool(read_config_str))):
            if negated_bool:
                val_true_false = str(not bool(strtobool(read_config_str)))
            else:
                val_true_false = str(bool(strtobool(read_config_str)))
    except ValueError:
        pass
    if val_true_false == "True":
        val_true_false = "Enabled"
    elif val_true_false == "False":
        val_true_false = "Disabled"
    return val_true_false

# =======================


def query_yes_no(question, default):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(qucolor(question) + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def confirm_run():
    answer = query_yes_no("\nDo you want continue to run?", None)
    if answer:
        return True
    else:
        message(2, "Canceled!")


def message(msg_code, msg):
    from pipeline import exec_menu
    if msg_code == 0:
        print "\n"+bcolors.OKBLUE + msg + bcolors.ENDC+"\n"
        raw_input("Please, press ENTER to continue ...")
        #exec_menu('')
    elif msg_code == 1:
        print bcolors.FAIL + msg + bcolors.ENDC+"\n"
    elif msg_code == 2:
        print bcolors.WARNING + msg + bcolors.ENDC+"\n"
        raw_input("Please, press ENTER to continue ...")
        #exec_menu('')
    elif msg_code == 3:
        print bcolors.OKGREEN + msg + bcolors.ENDC+"\n"
    elif msg_code == 4:
        print bcolors.NOTE + msg + bcolors.ENDC+"\n"
    return


def preparing_part():
    subprocess.call(['./src/bash/preparing.sh'])
    print(gcolor("Preparing to run..."))

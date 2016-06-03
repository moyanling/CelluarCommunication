# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 11:50:55 2016
@author: Jihan Chen
"""
import os, sys, logging, numpy
global content, location, TIME_STEP, t, shadowing_list  

t = 0
TIME_STEP = 1  # in s
CALL_ATTEMPT = 50
CALL_BLOCKED = 51
CALL_DROPS_S = 52
CALL_DROPS_C = 53
CALL_SUCCESS = 54
HANDOFF_ATTEMPT = 55
HANDOFF_SUCCESS = 56
HANDOFF_FAILURE = 57

description = [
'Call Attempt', 
'Call Blocked',
'Dropped (Low Signal Str)',
'Dropped (Not Enought Channel)',
'Call_Success',
'Handoff_Attempt',
'Handoff_Success',
'Handoff_Failed']

'''
For the element in the list, the first is number for alpha each hour, the second is the number for beta each hour.
The follow two are the total number for them every six hours.
And the final one is the string to formated for logging.
'''
info_dict = {
CALL_ATTEMPT: [0, 0, 0, 0, "<{0:d}s>[{1:s}] User# {2:d} attempts to make a call"],
CALL_DROPS_S: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] User# {2:d} is dropped because RSL {3:.2f} is lower than threshold"],
CALL_DROPS_C: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] User# {2:d} is dropped because no channel is available"],
CALL_BLOCKED: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] User# {2:d} is blocked. Try the other sector for help"],
CALL_SUCCESS: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] User# {2:d} call success"],
HANDOFF_ATTEMPT: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] There is a hand-off attempt for User# {2:d}."],
HANDOFF_SUCCESS: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] User# {2:d} successfully hand off to another sector"],
HANDOFF_FAILURE: [0, 0, 0, 0,  "<{0:d}s>[{1:s}] Hand off for User# {2:d} failed"] }

class Location:
    BASESTATION_X = 0  # x-coordinate of the basestation
    BASESTATION_Y = 0  # y-coordinate of the basestation
    USER_X = 20  # x-coordinate of users
    ALPHA_DIRECTION = [0, 1]  # Direction of alpha_direction
    BETA_DIRECTION = [(3 ** 0.5) / 2, -1 / 2]  # Direction of beta basestation
    ROAD_LENGTH = 6000  # in m
    ANTENNA_HEIGHT = 50  # in m
    MOBILE_HEIGHT = 1.5  # in m

class EnvCharacteristic:
    RX_THRESHOLD = -102  # in dBm    
    HANDOFF_MARGIN = 3  # in dB 
    CALL_RATE = 2 / 3600  # per second
    AVERAGE_CALL_DURATION = 180  # in second
    USER_NUM = 160
    CH_NUM = 15
    INIT_EIRP = 43 + 15 - 2

def _log_config():
    '''
    Config the log:
    Console is used to show INFO on console.
    '''
    #--------------------------------------------define levelname---------------------------------------
    logging.addLevelName(CALL_ATTEMPT, description[0])
    logging.addLevelName(CALL_BLOCKED, description[1])
    logging.addLevelName(CALL_DROPS_S, description[2])
    logging.addLevelName(CALL_DROPS_C, description[3])
    logging.addLevelName(CALL_SUCCESS, description[4])
    logging.addLevelName(HANDOFF_ATTEMPT, description[5])
    logging.addLevelName(HANDOFF_SUCCESS, description[6])
    logging.addLevelName(HANDOFF_FAILURE, description[7])
    #---------------------------------------------definition end----------------------------------------
    Console = logging.getLogger('Console')
    console = logging.StreamHandler(sys.stdout)
    Console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    Console.addHandler(console)
    
    Logger = logging.getLogger('Celluar.log')
    output_file = logging.FileHandler(mode='w', filename=os.path.join(os.getcwd(), 'Celluar.log'))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    output_file.setFormatter(formatter)
    Logger.addHandler(output_file)
    return Logger, Console
    
def logging_case(level, info):
    '''
    Used to log info according different case.
    '''
    if level == CALL_ATTEMPT:
        if info[0] == "Alpha":
            info_dict[CALL_ATTEMPT][0] += 1
            info_dict[CALL_ATTEMPT][2] += 1
        else:
            info_dict[CALL_ATTEMPT][1] += 1
            info_dict[CALL_ATTEMPT][3] += 1
        logger.log(CALL_ATTEMPT, info_dict.get(CALL_ATTEMPT)[-1].format(t, info[0], info[1]))
    elif level == CALL_DROPS_S:
        if info[0] == "Alpha":
            info_dict[CALL_DROPS_S][0] += 1
            info_dict[CALL_DROPS_S][2] += 1
        else:
            info_dict[CALL_DROPS_S][1] += 1
            info_dict[CALL_DROPS_S][3] += 1
        logger.log(CALL_DROPS_S, info_dict.get(CALL_DROPS_S)[-1].format(t, info[0], info[1], info[2]))
    else:
        if info[0] == "Alpha":
            info_dict[level][0] += 1
            info_dict[level][2] += 1
        else:
            info_dict[level][1] += 1
            info_dict[level][3] += 1
        logger.log(level, info_dict.get(level)[-1].format(t, info[0], info[1]))
        
'''
Read the "antenna_pattern.txt" and save the content
'''
with open("antenna_pattern.txt") as _f:
    content = _f.readlines()
    _f.close()
    del _f    


def new_shadowing_list():
    '''
    Shadowing_list is subjected to change in Q2 due to the change of road length, 
    This function is called to calculate a new shadowing list in that situation.
    '''
    return numpy.random.normal(0, 2, location.ROAD_LENGTH/10).tolist()

location = Location()
env_char = EnvCharacteristic()
logger, console = _log_config()
shadowing_list = new_shadowing_list()




if __name__ == '__main__':
    shadowing_list = new_shadowing_list()
    print(shadowing_list)
    
    
    
    
    
    
    
    
    
    
    
    
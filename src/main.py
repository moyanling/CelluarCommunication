# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 10:49:27 2016
@author: Jihan Chen
"""
import sys
sys.path.append('E:\Python\ENTS656\Project')

import numpy as np
from global_config import *
from classes import Basestation, MobileUser
import global_config as gc
import xlwt

'''
FYI:
For users who are making phone requests, in the program they are notated as 'caller'.
And for users who do not make phone request, they are notated as merely 'user'.
The coordinate of the basestation is (0, 0).
Thus, the coordinate of the user is (20, TBD)
'''
global alpha
global beta

alpha = Basestation("Alpha", 860, location.ALPHA_DIRECTION)
beta = Basestation("Beta", 865, location.BETA_DIRECTION) 
        
def update_user():
    '''
    Update those users and determine if the user makes a call request.
    If a user make a new call attempt, the following process is delegated to _new_call_attempt(user_id)
    '''
    # Traverse those who are not in caller_dict of both alpha and beta basestation.
    user_has_no_call = [i for i in range(env_char.USER_NUM) if i not in list(alpha.caller_dict) + list(beta.caller_dict)]
    for user_id in user_has_no_call:
        if np.random.binomial(1, env_char.CALL_RATE * TIME_STEP) == 0:
            continue  # Make no call request
        _new_call_attempt(user_id)  # Make a call request
        
def update_caller():
    '''
    Update the callers whose information are tracked in the basestation.
    First update the caller on alpha, then on beta.
    '''
    def _update_single_caller(user_id, serving_sector, backup_sector):
        caller = serving_sector.caller_dict[user_id]
        if caller.self_update() == 1:
            logging_case(CALL_SUCCESS, (serving_sector.name, user_id))
            serving_sector.del_caller(user_id)
            return
        serving_RSL = serving_sector.get_RSL(caller.y)     
        if serving_RSL < env_char.RX_THRESHOLD:
            logging_case(CALL_DROPS_S, (serving_sector.name, user_id, serving_RSL))
            serving_sector.del_caller(user_id)
            return
        backup_RSL = backup_sector.get_RSL(caller.y)   
        if backup_RSL >= (serving_RSL + env_char.HANDOFF_MARGIN):
            #----------------------------------- Potential hand-off ------------------------------------
            logging_case(HANDOFF_ATTEMPT, (serving_sector.name, user_id))
            if backup_sector.is_channel_available():
                backup_sector.add_caller(caller)
                serving_sector.del_caller(user_id)
                logging_case(HANDOFF_SUCCESS, (serving_sector.name, user_id))
            else:
                logging_case(HANDOFF_FAILURE, (serving_sector.name, user_id))
                
    caller_in_alpha = list(alpha.caller_dict)
    caller_in_beta = list(beta.caller_dict)
    for user_id in caller_in_alpha:
        _update_single_caller(user_id, alpha, beta)
    for user_id in caller_in_beta:
        _update_single_caller(user_id, beta, alpha)
    
def _new_call_attempt(user_id):
    '''
    Called when there is a new call attempt.
    The function determines the location, direction and other info for the user.
    Then it decide whether this call attempt will success or not.
    @param user_id: the user id.
    '''
    y = np.random.uniform(-location.ROAD_LENGTH/2, location.ROAD_LENGTH/2)  # Determine the location
    direction = "North" if np.random.binomial(1, 0.5) == 1 else "South"  # Determine the direction    
    a_RSL = alpha.get_RSL(y)  # RSL for alpha
    b_RSL = beta.get_RSL(y)  # RSL for beta
    # Select a serving sector for higher RSL and a bakcup sector
    serving_sector, backup_sector = (alpha, beta) if a_RSL >= b_RSL else (beta, alpha)         
    serving_RSL, backup_RSL = (a_RSL, b_RSL) if a_RSL >= b_RSL else (b_RSL, a_RSL)
    logging_case(CALL_ATTEMPT, (serving_sector.name, user_id))
    # Check RSL threshold for the selected serving sector
    if serving_RSL < env_char.RX_THRESHOLD:
        # Call dropped due to weak signal strength
        logging_case(CALL_DROPS_S, (serving_sector.name, user_id, serving_RSL))
    elif serving_sector.is_channel_available():
        serving_sector.add_caller(MobileUser(user_id, y, direction, np.random.exponential(env_char.AVERAGE_CALL_DURATION))) 
    else:    # No channel available for the selected serving sector.
        logging_case(CALL_BLOCKED, (serving_sector.name, user_id))
        # Try backup sector to help out.
        if backup_sector.is_channel_available() and backup_RSL > env_char.RX_THRESHOLD:
            # Backup sector successfully helped out.
            backup_sector.add_caller(MobileUser(user_id, y, direction, np.random.exponential(env_char.AVERAGE_CALL_DURATION)))            
        else:
            # Call dropped due to no capacity
            logging_case(CALL_DROPS_C, (serving_sector.name, user_id))

def _reset_every_hour():
    '''
    Reset those numbers in info_dict for every one hour's simulation.
    '''
    for key in info_dict:
        info_dict[key][0] = 0
        info_dict[key][1] = 0

def _reset_every_six_hour():
    '''
    Reset some necessary parameters after each simulation for six hours.
    Re-initiate an alpha and a beta instance to start a brand new simulation.
    '''
    _reset_every_hour()
    for key in info_dict:
        info_dict[key][2] = 0
        info_dict[key][3] = 0
    alpha = Basestation("Alpha", 860, location.ALPHA_DIRECTION)
    beta = Basestation("Beta", 865, location.BETA_DIRECTION) 
    gc.t = 0

def _write_excel(table, title, i, j = 0, bias = 0):
    '''
    @param table: An Excel work sheet
    @param i: row index
    @param j: col index
    @param title: The title for this report
    @param bias: int. An for the index. Should be either 0, for each hour's report, or 2 for six hours' summary.
    '''
    table.write(i, j, title)
    table.write(i, j+1, "Alpha")
    table.write(i, j+2, "Beta")
    for index in range(1, 9):
        table.write(i+index, j, gc.description[index - 1])
    for index in range(1, 9):
        table.write(i+index, j+1, info_dict[index + 49][0 + bias])
    for index in range(1, 9):
        table.write(i+index, j+2, info_dict[index + 49][1 + bias])
    table.write(i + 9, j, "Channel in use")
    table.write(i + 9, j + 1, env_char.CH_NUM - alpha.ch)
    table.write(i + 9, j + 2, env_char.CH_NUM - beta.ch)


def _stimulate_for_six_hours(table):
    '''
    Stimulate for six hours.
    The main process is to first call update_caller() then update_user() every second.
    At the end of each hour, record the cumulative number for different cases and reset those parameters for the next hour.
    @param table: the worksheet used to write information.
    '''
    for i in range(1, 7):
        while gc.t < 3600*i:
            update_caller()
            update_user()
            gc.t += 1
            #-------------------------------write Excel----------------------------
            if gc.t == 3600*i - 1:
                title = "Report for the " + str(i) + " th. hour:"
                row = (i - 1) * 11
                _write_excel(table, title, row)
                _reset_every_hour()
        _write_excel(table, "Summary", 66, bias = 2)
    _reset_every_six_hour()
    
            
def main():
    file = xlwt.Workbook()
    table1 = file.add_sheet('Q1', cell_overwrite_ok = True)
    table2 = file.add_sheet('Q2', cell_overwrite_ok = True)
    table3 = file.add_sheet('Q3', cell_overwrite_ok = True)
    table4 = file.add_sheet('Q4 3dB HOm', cell_overwrite_ok = True)
    table5 = file.add_sheet('Q4 0dB HOm', cell_overwrite_ok = True)
    table6 = file.add_sheet('Q4 5dB HOm', cell_overwrite_ok = True)
    
    table1.col(0).width=256 * 30
    table2.col(0).width=256 * 30
    table3.col(0).width=256 * 30
    table4.col(0).width=256 * 30
    table5.col(0).width=256 * 30
    table6.col(0).width=256 * 30
    #----------------------------Q1----------------------------
    _stimulate_for_six_hours(table1)
    file.save("report.xls")
    #----------------------------Q2----------------------------
    location.ROAD_LENGTH = 8000
    gc.shadowing_list = gc.new_shadowing_list()
    _stimulate_for_six_hours(table2)
    file.save("report.xls")
    #----------------------------Q3----------------------------
    location.ROAD_LENGTH = 6000
    gc.shadowing_list = gc.new_shadowing_list()
    env_char.USER_NUM = 320
    _stimulate_for_six_hours(table3)
    file.save("report.xls")
    #----------------------------Q4 3dB HOm----------------------------
    np.random.seed(42)
    env_char.HANDOFF_MARGIN = 3
    _stimulate_for_six_hours(table4)
    file.save("report.xls")
    #----------------------------Q4 0dB HOm----------------------------
    env_char.HANDOFF_MARGIN = 0
    _stimulate_for_six_hours(table5)
    file.save("report.xls")    
    #----------------------------Q4 5dB HOm----------------------------
    env_char.HANDOFF_MARGIN = 5
    _stimulate_for_six_hours(table6)
    file.save("report.xls")
    console.info("Mission Complete")




if __name__ == '__main__':
    main()  
    
    
    
    
    
    
    
    
    
    
    
    
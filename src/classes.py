# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 10:49:27 2016
@author: Jihan Chen
"""
import sys
sys.path.append('E:\Python\ENTS656\Project')

import numpy as np
from math import log10 as log
import global_config as gc

def ok_hata_propagation_loss(freq, distance, antenna_height = gc.location.ANTENNA_HEIGHT):
    '''
    Calculate the propagation loss according to the OK-Hata model.
    '''
    ahm = (1.1*log(freq)-0.7) * gc.location.MOBILE_HEIGHT - (1.56*log(freq) - 0.8)
    return 69.55+26.16*log(freq)-13.82*log(antenna_height)+(44.9-6.55*log(antenna_height))*log(distance/1000) - ahm
     
def shadowing(y):
    '''
    Read the shadowing_list in global_config according to the position of the user.
    '''
    return gc.shadowing_list[int(gc.location.ROAD_LENGTH/20) - int(y/10)]

def second_deepest_fading():
    '''
    @return: the second smallest fading in dB.
    '''
    a = np.random.normal(0, 1, 10)
    b = np.random.normal(0, 1, 10)
    fading_list = np.abs(a + b*(1j)).tolist()
    return 10*log(sorted(fading_list)[1])


class Basestation:
    '''
    Basestation Class. Module the behaviour of the basestation.
    '''   
    
    def __init__(self, name, freq, pointing_direction, eirp = gc.env_char.INIT_EIRP, ch = gc.env_char.CH_NUM):
        self.name = name
        self.freq = freq
        self.eirp = eirp
        self.ch = ch
        self.antenna_direction = pointing_direction
        self.caller_dict = {}
    
    def is_channel_available(self):
        assert 0 <= self.ch <= 15 
        return self.ch > 0
    
    def add_caller(self, caller):
        '''
        Establish a new call on the serving sector. This mainly involves:
        1. Channel number minus one;
        2. New entry is added to the caller_dict in MobileUser
        '''
        if not isinstance(caller, MobileUser):
            raise ValueError("The input should be a MobileUser instance.")
        assert 0 < self.ch <= 15
        self.caller_dict[caller.user_id] = caller
        self.ch -= 1
    
    def get_RSL(self, y):
        '''
        Calculate the receive signal level for a mobile in given distance.
        It equals to EIRP minus discrimination value, OK-Hata propagation loss, plus shadowing and fading.
        '''
        actual_eirp = self._get_eirp_in_direction(_get_angle(y, self.antenna_direction))
        ok_hata = ok_hata_propagation_loss(self.freq, _get_distance(y))
        return actual_eirp - ok_hata + shadowing(y) + second_deepest_fading()
        
        
    def del_caller(self, user_id):
        '''
        Delete the entry for a user according to the input user_id. This involves:
        1.Free a channel        
        2.Logging the case as a successful call.
        '''
        assert 0 <= self.ch < 15
        del self.caller_dict[user_id]
        self.ch += 1
    
    def _get_eirp_in_direction(self, angle):
        '''
        Return the value of the eirp after substracting the discrimination value.
        '''
        return self.eirp-float(gc.content[angle].split()[1])
        
def _get_angle(y1, antenna_direction, x1 = gc.location.USER_X):
    '''
    Calculate the angle between the direction the antenna is pointing and the direction pointing to the mobile.
    Two directions are notated in vector.
    '''
    vector_antenna = np.array(antenna_direction)
    length_va = np.sqrt(vector_antenna.dot(vector_antenna))
    vector_mobile = np.array([x1, y1])
    length_vm = np.sqrt(vector_mobile.dot(vector_mobile))
    angle = np.arccos(vector_antenna.dot(vector_mobile)/(length_va*length_vm))*360/2/np.pi
    return int(round(angle))            
    

def _get_distance(y1, y2 = gc.location.BASESTATION_Y, x1 = gc.location.USER_X, x2 = gc.location.BASESTATION_X):
    '''
    Return the distance between the basestation and the user.
    This function takes the Antenna height and mobile height into consideration.
    '''
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5        
    
        
class MobileUser:
    '''
    MobileUser Class. Module the behavior of mobiles and users. 
    '''
    
    def __init__(self, user_id, y, direction, call_duration ,v = 15, x = gc.location.USER_X):
        if y < -gc.location.ROAD_LENGTH/2 or y > gc.location.ROAD_LENGTH/2 or direction not in ["North", "South"]:
            raise ValueError("Invalid input. Y should indicate the position of the user on the road" +
            "and direction should either be 'North' or 'South'")
        self.user_id = user_id
        self.v = v
        self.x = x
        self.y = y
        self.direction = direction
        self.call_duration = call_duration
    
    def self_update(self):
        '''
        Update user's info for this user. This involves:
        The position of the user. i.e. y
        The call duration minus one. 
        The direction remains unchanged.
        @returns: 
            0: if update successfully.
            1: if call timer run out, or the user moves beyond the end of the road
        '''
        if self.direction is "North":
            self.y += self.v
        else:
            self.y -= self.v
        self.call_duration -= 1
        if self.call_duration <= 0 or self.y < -gc.location.ROAD_LENGTH/2 or self.y > gc.location.ROAD_LENGTH/2:
            return 1
        return 0
        

if __name__ == '__main__':
    alpha = Basestation("Alpha", 860, gc.location.ALPHA_DIRECTION)
    print(alpha.get_RSL(2000))
    print(int(gc.location.ROAD_LENGTH/20))











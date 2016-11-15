#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__      = "Peter Ogden"
__copyright__   = "Copyright 2016, Xilinx"
__email__       = "pynq_support@xilinx.com"

from unittest.mock import patch    
from collections import namedtuple
from collections import deque

from functools import wraps
from functools import reduce
import sys
import os
import re
import time
import pickle
import builtins
import pynq
import pytest

# Tuple for storing all information about an access to an object
Call = namedtuple('Call', 'action hash args kwargs ret')
# Make None the default for non-provided parameters
Call.__new__.__defaults__ = (None,) * len(Call._fields)
# Hack for pickling namedtuples inside of an IPython environment
# globals()[Call.__name__] = Call

MOCK_MODE_BYPASS = 0
MOCK_MODE_RECORD = 1
MOCK_MODE_PLAYBACK = 2

# Record buffer
record = []
# Playback buffer
playback = None
record_mode = MOCK_MODE_BYPASS
trace_dir = ''


if 'PYNQ_TEST_PLAYBACK_DIR' in os.environ:
    record_mode = MOCK_MODE_PLAYBACK
    trace_dir = os.environ['PYNQ_TEST_PLAYBACK_DIR']
elif 'PYNQ_TEST_RECORD_DIR' in os.environ:
    record_mode = MOCK_MODE_RECORD
    trace_dir = os.environ['PYNQ_TEST_RECORD_DIR']
    
# Objects listed here will not be wrapped with a Mock
def isprimitive(obj):
    return isinstance(obj, (str, int, float, bool, dict, list, type(None)))

# Contructs a new mock based on the current record mode
class Constructor:
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
    def __call__(self):
        if record_mode is MOCK_MODE_RECORD:
            return RecordMock(self.obj, self.name)
        elif record_mode is MOCK_MODE_PLAYBACK:
            return PlayMock(self.obj, self.name)
        else:
            return self.obj

def default_assertion(exp, act):
    assert(exp.hash == act.hash)
    assert(exp.args == act.args)
    assert(exp.kwargs == act.kwargs)
    return exp.ret

def normal_path(path):
    return os.path.split(path)[1]

ip_states = {}

def PL_load_ip_data_assertion(exp, act):
    global ip_states
    assert(exp.hash == act.hash)
    assert(exp.kwargs == act.kwargs)
    assert(len(exp.args) == len(act.args))
    for i in range(len(exp.args)):
        if i == 1:
           assert(normal_path(exp.args[i]) == normal_path(act.args[i]))
        else:
           assert(exp.args[i] == act.args[i])
    ip_states[act.args[0]] = act.args[1]
    return exp.ret

def PL_get_ip_state_assertion(exp, act):
    assert(exp.hash == act.hash)
    assert(exp.kwargs == act.kwargs)
    assert(exp.args == act.args)

    if act.args[0] in ip_states:
        return ip_states[act.args[0]]
    else:
        return None

def start_record():
    global record
    global record_mode
    record = []
    record_mode = MOCK_MODE_RECORD

def end_record(filename=None):
    if filename:
        with open(filename, 'wb') as f:
            pickle.dump(record, f, protocol=3)
        

def start_playback(filename=None):
    global playback
    global record_mode
    global ip_states
    if filename:
        with open(filename, 'rb') as f:
            playback = deque(pickle.load(f))
    else:
        playback = deque(record)
    record_mode = MOCK_MODE_PLAYBACK
    ip_states.clear()

def end_playback():
    assert (not playback)
    
    
normalisers = [(re.compile('.*PL.load_ip_data'), PL_load_ip_data_assertion),
               (re.compile('.*PL.get_ip_state'), PL_get_ip_state_assertion)]

class RecordMock:
    def __init__(self, obj, name = ''):
        self.wrapped_object = obj
        self.name = name
        record.append(Call(action='init', hash=hash(self), args=self.name, kwargs = None, ret = None))
        
    def __getattr__(self, name):
        new_obj = getattr(self.wrapped_object, name)
        if isprimitive(new_obj):
            record.append(Call(action='attr_prim',hash=hash(self),ret=new_obj,args=name, kwargs = None))
            return new_obj
        else:
            record.append(Call(action='attr',hash=hash(self),args=name,kwargs = None, ret = None))
            return RecordMock(new_obj, self.name + "." + name)
    
    def __call__(self, *args, **kwargs):
        new_obj = self.wrapped_object(*args, **kwargs)
        if isprimitive(new_obj):
            record.append(Call(action='call_prim',hash=hash(self),ret=new_obj,args=args,kwargs=kwargs))
            return new_obj
        else:
            record.append(Call(action='call',hash=hash(self),args=args,kwargs=kwargs,ret=None))
            return RecordMock(new_obj, self.name + '()')

    def __repr__(self):
        return 'RecordMock(obj={0}, name={1})'.format(repr(self.obj), self.name)

class PlayMock:
    def __init__(self, obj, name = ''):
        self.name = name
        call = playback.popleft()
        assert(call.action == 'init')
        assert(call.args == self.name)
        self.mapped_hash = call.hash
        self.assertion = default_assertion
        for p in normalisers:
            if p[0].match(name):
                self.assertion = p[1]
    
    def __getattr__(self, name):
        call = playback.popleft()
        assert(call.hash == self.mapped_hash)
        assert(call.args == name)
        if call.action == 'attr':
            return PlayMock(None, self.name + "." + name)
        elif call.action == 'attr_prim':
            return call.ret
        else:
            assert(False)
    
    def __call__(self, *args, **kwargs):
        expected = playback.popleft()
        actual = Call(hash = self.mapped_hash, args = args,
                      kwargs = kwargs, action = 'call')
        ret = self.assertion(expected, actual)
        if expected.action == 'call':
            return PlayMock(None, self.name + '()')
        elif expected.action == 'call_prim':
            return ret
        else:
            assert(False)

    def __repr__(self):
        return 'PlayMock(name={0})'.format(self.name)

# Helper function to find an object from a fully qualified python name
def str_to_object(string):
    parts = string.split('.')
    return reduce(getattr, parts, sys.modules[__name__])

def play_record(file, *patch_names):
    full_path = os.path.join(trace_dir, file)
    def decorator(func):
        @pytest.mark.skipif(record_mode is MOCK_MODE_PLAYBACK
                       and not os.path.isfile(full_path),
                       reason="No trace file found for test")
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            to_patch = patch_names
            if record_mode == MOCK_MODE_RECORD:
                start_record()
            elif record_mode == MOCK_MODE_PLAYBACK:
                start_playback(full_path)
            else:
                to_patch = []
            patchers = [patch(v, new_callable=Constructor(str_to_object(v), v))
                       for v in to_patch]
            for p in patchers:
                p.start()
                
            ret = func(*args, **kwargs)
            for p in patchers:
                p.stop()
            if record_mode == MOCK_MODE_RECORD:
                end_record(full_path)
            elif record_mode == MOCK_MODE_PLAYBACK:
                end_playback()
            return ret
        return wrapped_func
    return decorator


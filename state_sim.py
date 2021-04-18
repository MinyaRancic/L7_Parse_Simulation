import itertools
import re
from functools import partial

stored_int = 0
head_ptr = 0
tail_ptr = 0
mem = "" 
acc = 0
out_acc = 0
out_ready = 0
is_counting = 0
active_state = 0

def print_state(state):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    print("--STATE--")
    print("accumulator:" + str(acc))
    print("out acc:" + str(out_acc))
    print("out ready:" + str(out_ready))
    print("head ptr:" + str(head_ptr))
    print("tail ptr:" + str(tail_ptr))
    # print("current char:" + repr(mem[head_ptr]))
    print("stored int:" + str(stored_int))
    print("is_counting:" + str(is_counting))
    print("active_state: " + str(active_state))
    # if(out_ready):
    #     print("Matched: " + mem[head_ptr-out_acc:head_ptr])
    print()

# checks head_ptr to see if it is an instance of any of patterns
# if found, perform the passed in action
# also appropriately upate the state
# `active` informs which state the system needs to be in for this match
def match(state, patterns, action, active, result):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    if active_state != active:
        return state
    
    for pattern in patterns:
        if mem[head_ptr:head_ptr+len(pattern)] == bytes(pattern, "utf8"):
            state = action(state, pattern)
           # state[7] = result # set the active state
            (stored_int, head_ptr, tail_ptr, 
                acc, out_acc, out_ready, is_counting, active_state) = state
            active_state = result
            state =  (stored_int, head_ptr, tail_ptr, 
                acc, out_acc, out_ready, is_counting, active_state) 
    return state

def start_counting(state, pattern):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    if not is_counting:
        out_acc = acc
        out_ready = out_acc != 0
        acc = len(pattern)
        head_ptr += len(pattern)
        stored_int = 0
        is_counting = 1
    state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    return state

     
def end_counting(state, pattern):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    if is_counting:
        #print("ending count")
        #print(head_ptr)
        #print(repr(mem[head_ptr]))
        out_acc = acc + len(pattern) + stored_int
        out_ready = 1
        acc = 0
        active_state = 0
        is_counting = 0
        # have to move the head_ptr up - is this universally true?
        head_ptr += len(pattern) + stored_int
        stored_int = 0
    state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    return state 

def add_num(state, pattern):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    if is_counting:
        acc += len(pattern)
        head_ptr = head_ptr + len(pattern)
        match = re.search("\d+", mem[head_ptr::].decode("utf8", "replace"))
        stored_int = int(match.group(0))
    state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    return state

def nop(state, pattern):
    (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = state
    if is_counting:
        acc += len(pattern)
        head_ptr = head_ptr + len(pattern)
    state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    return state

def get_furthest_state(states):
    furthest = states[0]
    furthest_head = furthest[1]
    for state in states:
        (stored_int, head_ptr, tail_ptr, 
                acc, out_acc, out_ready, is_counting, active_state) = state
        if head_ptr > furthest_head:
            furthest = state
            furthest_head = state[1] 
    return furthest

# with open("payload.pop3", "r", newline='') as myfile:
#     mem = myfile.read()

# tail_ptr = len(mem) - 1
### POP3 Implementation ###
# while head_ptr < tail_ptr:
#     #scan_begin(["OPTIONS", "GET", "HEAD", "POST",
#     #            "PUT", "TRACE", "DELETE", "CONNECT"])
#     #scan_end("\r\n\r\n")
#     state = (stored_int, head_ptr, tail_ptr, 
#              acc, out_acc, out_ready, is_counting)
#     state_1 = match(state, ["USER", "PASS", "STAT", "LIST",
#                 "RETR", "DELE", "RSET", "TOP", "QUIT"], start_counting)
#     state_2 = match(state, ["\r\n"], end_counting)
#     # state update logic, pick the state that is furthest ahead
#     # default case, no match succeeded (might be easier w/ metadata)
#     next_state = get_furthest_state([state, state_1, state_2])
#     if state == next_state:
#         head_ptr += 1
#         acc += 1
#         state = (stored_int, head_ptr, tail_ptr, 
#              acc, out_acc, out_ready, is_counting)
#     else: 
#         (stored_int, head_ptr, tail_ptr, 
#              acc, out_acc, out_ready, is_counting) = next_state
#     if out_ready == 1:
#         print(out_acc)
#         out_ready = 0
#     # print_state(next_state)

with open("payload.http", "rb") as myfile:
    mem = myfile.read()

tail_ptr = len(mem) - 1

while head_ptr < tail_ptr:
    state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    state_1 = match(state, ["GET ", "POST ", "OPTIONS ", "HEAD ", "PUT ", "TRACE ", "DELETE ", "CONNECT ", "HTTP/1.1 "], start_counting, 0, 0)
    state_2 = match(state, ["Content-Length:"], add_num, 0, 1)
    state_3 = match(state, ["Transfer-Encoding: chunked"], nop, 0, 2)
    state_4 = match(state, ["Transfer-Encoding: chunked"], nop, 1, 2)
    state_5 = match(state, ["\r\n\r\n"], end_counting, 0, 0)
    state_6 = match(state, ["\r\n\r\n"], end_counting, 1, 0)
    state_7 = match(state, ["0\r\n"], end_counting, 2, 0)
    # state update logic, pick the state that is furthest ahead
    # default case, no match succeeded (might be easier w/ metadata)
    next_state = get_furthest_state([state, state_1, state_2, state_3, state_4, state_5, state_6, state_7])
    if state == next_state:
        head_ptr += 1
        acc += 1
        state = (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state)
    else:
        (stored_int, head_ptr, tail_ptr, 
             acc, out_acc, out_ready, is_counting, active_state) = next_state
    if out_ready == 1:
        print(out_acc)
        out_ready = 0
    if mem[head_ptr:head_ptr+1] == "co":
        print(mem[head_ptr::])
    # print_state(next_state)
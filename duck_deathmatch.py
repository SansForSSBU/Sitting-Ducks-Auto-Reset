import os
import psutil
import pymem
import pymem.ptypes
import time
import threading
os.chdir("C:\Program Files (x86)\Sitting Ducks US 2005")

mode = 2
game = "US"
test_time = 60.0 # seconds to test ducks for
ducks = []
best_duck = None
best_dilation = 0.0
dilation_threshold = None

def make_duck():
    os.startfile("C:\Program Files (x86)\Sitting Ducks US 2005\overlay.exe")
    
def find_ducks():
    pids = psutil.pids()
    ducks = [pid for pid in pids if psutil.Process(pid).name()=="overlay.exe"]
    return ducks

def kill_duck(duck_pid):
    psutil.Process(duck_pid).terminate()
        
def get_ducktime(duck_pid):
    if (game == "US"):
        offset_1 = 0x1D5A50
        offset_2 = 0x26DC
    if (game == "EU"):
        offset_1 = 0x1D5A40
        offset_2 = 0x26DC
    duck_mem = pymem.Pymem(duck_pid)
    base_addr = duck_mem.base_address
    ptr_1 = base_addr + offset_1
    ptr_2 = pymem.ptypes.RemotePointer(duck_mem.process_handle, ptr_1)
    duck_time = duck_mem.read_float(ptr_2.value + offset_2)
    return duck_time

def test_duck(duck_pid):
    ducktime_before = get_ducktime(duck_pid)
    time.sleep(test_time)
    ducktime_after = get_ducktime(duck_pid)
    dilation = (ducktime_after - ducktime_before) / test_time
    return dilation

def duck_deathmatch(duck_pid_list):
    ducktimes_before = {}
    best_dilation = 0.0
    best_duck = None
    for duck_pid in duck_pid_list:
        ducktimes_before[duck_pid] = get_ducktime(duck_pid)
    time.sleep(test_time)
    for duck in ducktimes_before.keys():
        dilation = (get_ducktime(duck) - ducktimes_before[duck]) / test_time
        if dilation > best_dilation:
            if best_duck != None:
                kill_duck(best_duck)
            best_duck = duck
            best_dilation = dilation
        else:
            kill_duck(duck)
    print("Best dilation: ", best_dilation)
    print("Best PID: ", best_duck)
    if (dilation_threshold != None):
        if (best_dilation > dilation_threshold):
            print("Reached threshold, exiting")
            quit()
    

def duck_thread():
    global best_dilation
    global best_duck
    duck_list_before = find_ducks()
    make_duck()
    time.sleep(duck_finding_delay)
    duck_list_after = find_ducks()
    new_ducks = [duck for duck in duck_list_after if not (duck in duck_list_before)]
    if len(new_ducks) != 1:
        raise Exception("I've lost track of the ducks!")
    new_duck = new_ducks[0]
    time.sleep(duck_testing_delay)
    dilation = test_duck(new_duck)
    print(new_duck, dilation)
    if dilation > best_dilation:
        if (best_duck != None):
            kill_duck(best_duck)
        best_duck = new_duck
        best_dilation = dilation
        print("New best: ", dilation)
    else:
        kill_duck(new_duck)

def endless_duck_tourney():
    while True:
        thr = threading.Thread(target=duck_thread)
        thr.start()
        time.sleep(duck_creation_interval)


if mode == 0:
    duck_deathmatch(find_ducks())

if mode == 2:
    while True:
        for i in range(20):
            make_duck()
        time.sleep(20)
        duck_deathmatch(find_ducks())
        time.sleep(10)

duck_creation_interval = 15.0 # seconds between making new ducks
duck_finding_delay = 1.0 # seconds before trying to find new duck
duck_testing_delay = 20.0 # seconds before starting the test
if mode == 1:
    endless_duck_tourney() # TODO: this doesn't work!
        
    


    



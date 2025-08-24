from NekoMimi import utils as nm
from NekoMimi.consoleToys import kprint as kp
from mastodon import Mastodon
from markdownify import markdownify as md
import requests
import json 
import time

class PALLET:
    STRONG= "#fcfcff"
    MIDTEXT= "#898988"
    ERROR= "#ee2288"

def request_input():
    while True:
        try:
            get_req= input()
            get_req= int(get_req)
            if get_req > 6 or get_req < 1:
                kp("No me lord, not more than six or less than one... >", PALLET.ERROR, False)
                continue
            break
        except:
            kp("No me lord, we request numbers only... >", PALLET.ERROR, False)
    return get_req

def main_proc():
    kp(nm.figlet("CaptainToot"))
    kp("Sailing the seas hunting for toots reaped by hooks that do not discord on the tresure location", PALLET.MIDTEXT)
    kp("What shall your destination be, sayeth the name of the sea, our ship awaits the command of thee", PALLET.MIDTEXT)
    kp("")
    kp("> 1     Start sailing")
    kp("> 2     Write map")
    kp("> 3     Reset map")
    kp("> 4     Write hook")
    kp("> 5     Reset hook")
    kp("> 6     Catch up with updates")
    kp("")
    kp("Your words me lord? >", newline= False)
    operation= request_input()

if __name__ == "__main__":
    main_proc()

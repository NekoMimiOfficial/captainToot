import sys
import time
from mastodon import Mastodon
from NekoMimi import reg
from NekoMimi import utils as nm
from NekoMimi import consoleToys as ct
from mastodon.internals import requests
from mastodon.streaming import json
from markdownify import markdownify as md

__version__= "0.2";

class WebHookData:
    def __init__(self):
        self.title= "Mastodon post";
        self.description= "Description of the toot\ncontains very important data\nTOS invalidated lol :3";
        self.url= "https://github.com/NekoMimiOfficial"
        self.footer= "Neko's CaptainToot at your service";
        self.timestamp= "2004-02-10T12:00:00.000Z";
        self.image= "http://nekomimi.tilde.team/API/v1/res/NekoMimiV4.2.png";
        self.icon= "http://nekomimi.tilde.team/API/v1/res/NekoMimiV4.2.png";
        self.color= 5814783;

def _format_webhook(d: WebHookData):
    content= {
      "content": "",
      "embeds": [
        {
          "title": d.title,
          "url": d.url,
          "description": d.description,
          "color": d.color,
          "fields": [],
          "footer": {"text": d.footer},
          "timestamp": d.timestamp,
          "image": {"url": d.image},
          "thumbnail": {"url": d.icon}
        }
      ],
      "attachments": []
    }

    return json.dumps(content);

def debug_sym(txt: str)-> None:
    if "--dbg" in sys.argv:
        print("[DEBUG] "+txt);

def _send_webhook(wh: str, d: WebHookData):
    postRQ= requests.post(url= wh, headers= {"Accept" : "application/json", "Content-Type" : "application/json"}, data= _format_webhook(d));
    return postRQ;

def initDB(DB: reg.Database):
    count= int(DB.query("acc-count"));
    while count > 0:
        i= DB.query(f"acc-i-{count}");
        u= DB.query(f"acc-u-{count}");

        if reg.readCell("captainToot") == "Registry uninitialized, please use the neko shell to initialize it":
            ct.kprint("[Auth Error] Please add API key using the NekoMimi shell and the cell name \"captainToot\"", "#ff2288");
            exit(1);
        if reg.readCell("captainToot").startswith("cell: "):
            ct.kprint("[Auth Error] Please add API key using the NekoMimi shell and the cell name \"captainToot\"", "#ff2288");
            exit(1);
        API= Mastodon(api_base_url= i, access_token= reg.readCell("captainToot"));
        try:
            user_id= API.account_lookup(u)["id"];
            last_status_id= API.account_statuses(id= user_id)[0]["id"];
            DB.store(f"acc-s-{count}", str(last_status_id));
        except Exception as e:
            ct.kprint(f"[API Error] failed to initialize DB, failed to lookup user_id: [{u}], err: [{e}]", "#ff2288");

        count = count - 1;

class CTIO:
    def __init__(self):
        self.i= "";
        self.u= "";
        self.d= "";
        self.s= "";
        self.icon_url= "";
        self.full_name= "";
        self.index= "";

def _get_acc(DB: reg.Database):
    count= int(DB.query("acc-count"));
    accounts: list[CTIO]= []
    while count > 0:
        acc_holder= CTIO();
        i= DB.query(f"acc-i-{count}");
        u= DB.query(f"acc-u-{count}");
        d= DB.query(f"acc-d-{count}");
        s= DB.query(f"acc-s-{count}");

        if reg.readCell("captainToot") == "Registry uninitialized, please use the neko shell to initialize it":
            ct.kprint("Please add API key using the NekoMimi shell and the cell name \"captainToot\"", "#ff2288");
            exit(1);
        if reg.readCell("captainToot").startswith("cell: "):
            ct.kprint("Please add API key using the NekoMimi shell and the cell name \"captainToot\"", "#ff2288");
            exit(1);
        API= Mastodon(api_base_url= i, access_token= reg.readCell("captainToot"));
        try:
            url_pfp= API.account_lookup(u)["avatar_static"];
            full_name= API.account_lookup(u)["display_name"];

            acc_holder.index= str(count);
            acc_holder.i= i;
            acc_holder.u= u;
            acc_holder.d= d;
            acc_holder.s= s;
            acc_holder.icon_url= url_pfp;
            acc_holder.full_name= full_name;

            accounts.append(acc_holder);
        except Exception as e:
            ct.kprint(f"[API Error] failed getting account: [{u}], failed to lookup pfp and name, err: [{e}]", "#ff2288");
        count = count - 1;

    return accounts;



def _more_add()-> str:
        ct.kprint("Add more accounts? [y/n]: ", "#ffff88", False);
        addResp= input().lower();
        return addResp

class CTS:
    def __init__(self):
        self.m_instance= "";
        self.m_user= "";
        self.d_webhook= "";

def initAPP(DB: reg.Database):
    ct.kprint("First run init", "#0088ff");

    saves: list[CTS]= [];
    stop= True
    while stop:
        ct.kprint("[instance] >", "#aaff88", False);
        mastoInstance= input();
        ct.kprint("[username] >", "#aaff88", False);
        mastoUsername= input();
        ct.kprint("[Discord webhook] >", "#aaff88", False);
        discoHook= input();

        c_save= CTS();
        c_save.m_instance= mastoInstance;
        c_save.m_user= mastoUsername;
        c_save.d_webhook= discoHook;
        saves.append(c_save);

        while True:
            addResp= _more_add();
            if addResp == "n":
                stop= False;
                break;
            if addResp == "y":
                break;

    i= 0;
    DB.store("acc-count", f"{str(len(saves))}");
    while i<len(saves):
        DB.store(f"acc-i-{i+1}", saves[i].m_instance);
        DB.store(f"acc-u-{i+1}", saves[i].m_user);
        DB.store(f"acc-d-{i+1}", saves[i].d_webhook);
        i += 1;

    DB.store("first_run", "1");
    return;

class StatusData:
    def __init__(self):
        self.id= "";
        self.url= "";
        self.body= "";
        self.image= "";
        self.timestamp= "";

def _timestampify(tsmf: str)-> str:
    return str(tsmf).split("+", 1)[0].replace(" ", "T")+"Z";

def _bodify(rbod: str)-> str:
    #truncate to 2000 characters
    rbod= rbod[:1998];
    i= 0;
    bod_lin= rbod.split("\n");
    debug_sym("[bodify] body:\n"+str(bod_lin));
    #replace h1 style
    while i < (len(bod_lin)-3):
        debug_sym(f"[bodify] body length: {len(rbod)}, lines: {len(bod_lin)}, iterator: {i}");
        if bod_lin[i+1].startswith("="):
            if bod_lin[i+1] == ("="*len(bod_lin[i])):
                debug_sym(f"[bodify] removing line: {i}, head: '{bod_lin[i]}, decoration: '{bod_lin[i+1]}'")
                bod_lin[i]= f"# {bod_lin[i]}"
                bod_lin.pop(i+1)

        i= i + 1
    rbod_f= ""
    for line in bod_lin:
        rbod_f= rbod_f + line + "\n"
    return rbod_f;

def worker(DB: reg.Database):
    if DB.query("acc-s-1") == "":
        initDB(DB);

    while True:
        accs= _get_acc(DB);
        for acc in accs:
            MPI= Mastodon(access_token= reg.readCell("captainToot"), api_base_url= acc.i);
            try:
                uid= MPI.account_lookup(acct= acc.u)["id"];
                statuses= MPI.account_statuses(id= uid, min_id= acc.s);
            except Exception as e:
                ct.kprint(f"[API Error] failed getting statuses for account: [{acc.u}], failed to query api for statuses, err: [{e}]", "#ff2288");
                statuses= []
            for status in statuses:
                SD= StatusData();
                SD.id= status["id"];
                SD.timestamp= _timestampify(status["created_at"]);
                SD.url= status["url"];
                SD.body= md(status["content"]);
                if "media_attachments" in status:
                    for atch in status["media_attachments"]:
                        if atch["type"] == "image":
                            SD.image= atch["url"];
                            break;

                WD= WebHookData();
                WD.title= acc.full_name;
                WD.url= SD.url
                WD.description= _bodify(SD.body);
                WD.icon= acc.icon_url;
                WD.image= SD.image;
                WD.timestamp= SD.timestamp;
                WD.footer= f"bridged via CaptainToot v{__version__}";

                RQ= _send_webhook(acc.d, WD);
                print(f"Request to send WH to Discord [{RQ.status_code}]");
                print(WD.title);
                print(WD.description);
                print(WD.url);
                print(WD.image);
                print(WD.timestamp);
                print(SD.id);
                print("===================================");

                if RQ.status_code == 204:
                    DB.store(f"acc-s-{acc.index}", str(SD.id));

        time.sleep(10);
    
def main_proc():
    ct.kprint(nm.figlet("CaptainToot", "small"), "#ffddff");
    DB= reg.Database("captainToot");
    first_run= DB.query("first_run");
    if not first_run == "1":
        initAPP(DB);
    
    elif "--reset" in sys.argv:
        DB.store("first_run", "0");
        count= int(DB.query("acc-count"));
        while count > 0:
            DB.store(f"acc-s-{count}", "");
        ct.kprint("Database reset successfully, setup will run on next start", "#0088ff");
        exit(0);

    elif "--refresh-latest-ids" in sys.argv:
        ct.kprint("Refreshing latest status IDs...", "#0088ff");
        initDB(DB);

    worker(DB);

if __name__ == "__main__":
    main_proc();

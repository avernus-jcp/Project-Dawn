import os
import sys
sys.path.insert(0,os.getcwd())

import json
import wget
import time
import datetime
import traceback

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

import urllib
from urllib.request import urlopen

from pathlib import Path

import shutil

import platform

def Notify(msg):
    return messagebox.showinfo(title=None, message=msg)

class JsonConfig:
    def __init__(self, dir='manifest.json'):
        self.Path = Path(dir)
        self.Decode()
    def Decode(self):
        self.Table = json.loads(self.Path.read_text())
        return self.Table
    def Encode(self):
        return json.dumps(self.Table, indent=4)
    def __getitem__(self, item):
        try:
            return self.Table[item]
        except Exception as e:
            return False
    def __setitem__(self, item, value):
        self.Table[item] = value
        self.Write()
    def Write(self):
        self.Path.write_text(self.Encode())

def Minecraft():
    return JsonConfig()["minecraft"]        

class GitManager:
    def __init__(self, repo='TheMerkyShadow/Project-Dawn'):
        self.Repo = repo
        self.Config = JsonConfig()        
    def APIGateway(self, api):
        url = ( 'https://api.github.com/repos/' )
        url += ( self.Repo +api )
        try:              
            return json.load(urlopen(url))
        except urllib.error.URLError as e:
            Notify( traceback.format_exc() )
    def Latest(self):
        return self.APIGateway('/branches/main')['commit']['sha']
    def Diff(self):
        self.Old = self.Config['commit']        
        self.New = self.Latest()
        if not self.Old.isalnum():
            self.Old = self.New        
        if self.Old == self.New:
            return None
        return self.APIGateway('/compare/' + self.Old + '...' + self.New)['files']
    def Sync(self):
        Notify( "Verification Started" )
        diff = self.Diff()
        if diff:
            for info in diff:
                path = Path( info["filename"] )
                url = info["raw_url"]
                url = url.replace("%20", " ") #weird git space bug in url
                if path.name == "dawn.exe":
                    continue
                
                parent = path.parent
                parent.mkdir(parents=True, exist_ok=True)

                status = info["status"]
                try:
                    if status == "added" or status == "modified":
                        temp = Path( wget.download(url) )
                        temp.replace(path)
                    elif status == "renamed":
                        previous = Path( info["previous_filename"] )
                        if previous.is_file():
                            previous.rename(path)                        
                    elif status == "removed":
                        if path.is_file():
                            path.unlink()
                        if parent.is_dir():
                            empty = list(os.scandir(parent)) == 0
                            if empty:
                                parent.rmdir()
                                
                except Exception as e:
                    print( "ERROR:", status, path )
                    Notify( traceback.format_exc() )
                    sys.exit()
                    
                print( status, path )
                
        self.Config.Decode()
        self.Config["commit"] = self.New
        self.Config["last"] = str(datetime.datetime.now())
        Notify("Verification Complete" ) 
        return
    
if __name__ == '__main__':
    import menu

import os
import sys
import win32com.client

class Shortcut:
    def __init__(self, file_to_run, args="", name="shortcut", icon=""):
        self.file = os.path.abspath(file_to_run)
        self.args = args
        self.name = name
        self.icon = os.path.abspath(icon) if icon else ""

    def create(self, dest_folder="."):
        shell = win32com.client.Dispatch("WScript.Shell")
        path = os.path.join(os.path.abspath(dest_folder), f"{self.name}.lnk")
        lnk = shell.CreateShortCut(path)
        
        lnk.Targetpath = sys.executable
        lnk.Arguments = f'"{self.file}" {self.args}'
        lnk.WorkingDirectory = os.path.dirname(self.file)
        
        if self.icon:
            lnk.IconLocation = self.icon
            
        lnk.Save()
        return path


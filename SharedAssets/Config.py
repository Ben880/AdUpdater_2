# ==========================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ==========================================================================
# Description:
# Handles loading json files into a key-pair dictionary and stores for access
# Can add vals and write but does not do so in this project
# ==========================================================================
import json
import os


class Config:

    dir_path = os.path.dirname(os.path.realpath(__file__))
    appFolder = os.path.join(dir_path, "config")
    cfgName = "cfg.json"
    data = {}

    def __init__(self, configFile = "cfg.json", fileDir = "Config"):
        self.setFile(configFile, fileDir)

    def setFile(self, filename, fileDir):
        self.cfgName = filename
        self.appFolder = fileDir

    def genFile(self):
        self.data = {
            "projectName": "AdUpdater_2",
        }
        self.write()

    def load(self):
        if not os.path.isdir(self.appFolder):
            print("No app folder: Making one")
            os.mkdir(self.appFolder)
        if not os.path.isfile(os.path.join(self.appFolder, self.cfgName)):
            print("No app cfg: Making one {}".format(os.path.join(self.appFolder, self.cfgName)))
            self.genFile()
        cfg = open(os.path.join(self.appFolder, self.cfgName), "r")
        self.data = json.load(cfg)
        cfg.close()

    def write(self):
        with open(os.path.join(self.appFolder, self.cfgName), 'w+') as fp:
            fp.write(json.dumps(self.data, sort_keys=True, indent=4))

    def setVal(self, key, val):
        self.data[key] = val

    def getVal(self, key):
        return self.data[key]

    def contains(self, key):
        return key in self.data

    def addVal(self, key, value):
        self.data[key] = value
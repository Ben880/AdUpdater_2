# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Holds some globally used variables
# ======================================================================================================================

import os
from SharedAssets.ClientList import ClientList
from SharedAssets.Config import Config


client_list = ClientList()
working_directory = os.getcwd()
config = Config(configFile="servercfg.json", fileDir=os.path.join(working_directory, "Config"))
config.load()


power_point_dir = os.path.join(working_directory, config.getVal("power_point_dir"))


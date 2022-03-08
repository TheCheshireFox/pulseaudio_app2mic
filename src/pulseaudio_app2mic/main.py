#!/bin/env python3

# You may need to set in /etc/openal/alsoft.conf
# 
# [pulse]
# allow-moves=true
#
# as openal (idk why) by default set DONT_MOVE flag for app inputs

from .rerouting_manager import ReroutingManager
from .task_bar_icon_app import TaskBarIconAppQt


def main():
    with ReroutingManager() as rerouting_manager:
        app = TaskBarIconAppQt(rerouting_manager)
        app.run()

if __name__ == '__main__':
    main()
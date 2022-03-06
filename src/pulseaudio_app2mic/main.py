#!/bin/env python3

# You may need to set in /etc/openal/alsoft.conf
# 
# [pulse]
# allow-moves=true
#
# as openal (idk why) by default set DONT_MOVE flag for app inputs

import wx.adv

from .rerouting_manager import ReroutingManager
from .task_bar_icon import TaskBarIcon


class App(wx.App):
    def __init__(self, rerouting_manager: ReroutingManager, *args, **kwargs):
        self._rerouting_manager = rerouting_manager

        super().__init__(*args, **kwargs)

    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame, self._rerouting_manager)
        return True


def main():
    with ReroutingManager() as rerouting_manager:
        app = App(rerouting_manager, False)
        app.MainLoop()

if __name__ == '__main__':
    main()
import wx.adv
from typing import Callable


class TaskBarMenu:
    def __init__(self, on_exit_cb: Callable[[wx.CommandEvent], None]):
        self._menu = wx.Menu()
        self._apps_menu = wx.Menu()
        self._on_exit = on_exit_cb

    def set_apps_menu(self, apps: list[str], checked_apps: list[str], callback: Callable[[str], None]):
        for app_name in apps:
            label = app_name if len(app_name) < 16 else app_name[:16]

            item = wx.MenuItem(parentMenu=self._apps_menu, id=wx.ID_ANY, text=label, kind=wx.ITEM_CHECK)
            self._apps_menu.Bind(wx.EVT_MENU, lambda evt: callback(app_name), id=item.GetId())

            self._apps_menu.Append(item)

            if checked_apps and app_name in checked_apps:
                item.Check(True)
            
        self._menu.Append(wx.ID_ANY, 'Applications', self._apps_menu)
        self._menu.AppendSeparator()

        item = wx.MenuItem(self._menu, -1, 'Exit')
        self._menu.Bind(wx.EVT_MENU, self._on_exit, id=item.GetId())
        self._menu.Append(item)
    
    @property
    def menu(self):
        return self._menu
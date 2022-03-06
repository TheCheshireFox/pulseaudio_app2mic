import wx.adv

from .task_bar_menu import TaskBarMenu
from .rerouting_manager import ReroutingManager


TRAY_ICON = '/usr/share/icons/breeze/actions/24/player-volume.svg'


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame, rerouting_manager: ReroutingManager):
        self.frame = frame
        self._rerouting_manager = rerouting_manager

        super(TaskBarIcon, self).__init__()
        icon = wx.Icon(wx.Bitmap(TRAY_ICON, wx.BITMAP_TYPE_ANY))

        self.SetIcon(icon, '')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def _show_info(self, text: str):
        wx.MessageDialog(self.frame, text, 'Pulseaudio App2Mic', wx.OK|wx.STAY_ON_TOP|wx.CENTRE|wx.ICON_INFORMATION).ShowModal()

    def _show_error(self, text: str):
        wx.MessageDialog(self.frame, text, 'Pulseaudio App2Mic', wx.OK|wx.STAY_ON_TOP|wx.CENTRE|wx.ICON_ERROR).ShowModal()

    def CreatePopupMenu(self):
        menu = TaskBarMenu(self.on_exit)
        menu.set_apps_menu(self._rerouting_manager.list_apps(), self._rerouting_manager.list_reroutings(), self.on_app_click)

        return menu.menu

    def on_app_click(self, app_name):
        if self._rerouting_manager.is_rerouted(app_name):
            try:
                self._rerouting_manager.disable_rerouting(app_name)
                self._show_info(f'Application {app_name} routing removed')
            except:
                self._show_error(f'Uanble to remove routing for application {app_name}\nSee logs for more info')
        else:
            try:
                virt_mic = self._rerouting_manager.enable_rerouting(app_name)
                self._show_info(f'Application {app_name} microphone available as {virt_mic}')
            except:
                self._show_error(f'Uanble to reroute application {app_name}\nSee logs for more info')

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, '')

    def on_left_down(self, event):
        pass

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()
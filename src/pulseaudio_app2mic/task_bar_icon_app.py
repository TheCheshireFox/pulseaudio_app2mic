import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox, QMenu, QAction

from .rerouting_manager import ReroutingManager


TRAY_ICON = os.path.join(os.path.dirname(__file__), 'icons', 'tray_white.svg')


class TaskBarIconAppQt():
    def __init__(self, rerouting_manager: ReroutingManager):
        self._rerouting_manager = rerouting_manager

        self._app = QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

        self._tray = QSystemTrayIcon(QIcon(TRAY_ICON), self._app)
        self._tray.setVisible(True)
        self._tray.show()

        self._tray.activated.connect(self._on_activate)

        self._menu = None
        self._show_menu = True
    
    def _show_info(self, text: str):
        QMessageBox(QMessageBox.Icon.Information, 'Pulseaudio App2Mic', text, QMessageBox.StandardButton.Ok).exec()

    def _show_error(self, text: str):
        QMessageBox(QMessageBox.Icon.Critical, 'Pulseaudio App2Mic', text, QMessageBox.StandardButton.Ok).exec()

    def _on_app_selected(self, app_name: str):
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

    def _on_activate(self, reason: QSystemTrayIcon.ActivationReason):
        if self._show_menu:
            self._show_menu = False

            self._menu = QMenu()

            apps = self._rerouting_manager.list_apps()
            rerouted_apps = self._rerouting_manager.list_reroutings()

            def create_app_cb(app_name: str):
                def on_action(checked: bool):
                    return self._on_app_selected(app_name)
                return on_action

            for app in apps:
                action = QAction(app, self._menu, checkable=True, checked=app in rerouted_apps)
                action.triggered.connect(create_app_cb(app))
                self._menu.addAction(action)
            
            exit_action = QAction('Exit', self._menu)
            exit_action.triggered.connect(self._app.quit)
            self._menu.addSeparator()
            self._menu.addAction(exit_action)

            self._tray.setContextMenu(self._menu)
        else:
            self._tray.setContextMenu(None)
            self._show_menu = True

    def run(self):
        self._app.exec_()
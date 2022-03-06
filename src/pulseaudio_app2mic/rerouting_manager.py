import pulsectl

from .pulse_rerouting import Rerouting, VirtSink, VirtSource

class ReroutingManager:
    def __init__(self):
        self._reroutings: dict[str, Rerouting] = {}
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for rerouting in self._reroutings.values():
            try:
                rerouting.cleanup()
            except:
                pass

    def _init_reroiting(self, app_name: str):
        try:
            pulse_app_name = app_name.lower().replace(' ', '').replace('\t', '')
            reroiting = Rerouting(
                VirtSink(f'{pulse_app_name}-speaker'),
                VirtSink(f'{pulse_app_name}-internal-speaker'),
                VirtSource(f'{pulse_app_name}-internal-mic'),
                VirtSource(f'{pulse_app_name}-mic'))
            
            reroiting.init()
            reroiting.route(app_name)
            self._reroutings[app_name] = reroiting

            self._show_info(f'Application {app_name} microphone available as {pulse_app_name}-mic')
        except Exception as e:
            self._show_error(f'Uanble to reroute application {app_name}\nSee logs for more info')

    def _cleanup_rerouting(self, app_name: str):
        try:
            self._reroutings.pop(app_name).cleanup()
            self._show_info(f'Application {app_name} routing removed')
        except Exception as e:
            self._show_error(f'Uanble to remove routing for application {app_name}\nSee logs for more info')

    def list_apps(self):
        with pulsectl.Pulse() as pulse:
            return [s.proplist['application.name'] for s in filter(lambda s: 'application.name' in s.proplist, pulse.sink_input_list())]

    def list_reroutings(self) -> list[str]:
        return self._reroutings.keys()
    
    def is_rerouted(self, app_name: str):
        return app_name in self._reroutings

    def enable_rerouting(self, app_name: str) -> str:
        if app_name in self._reroutings:
            raise Exception(f'Application {app_name} already rerouted')
        
        pulse_app_name = app_name.lower().replace(' ', '').replace('\t', '')
        reroiting = Rerouting(
            VirtSink(f'{pulse_app_name}-speaker'),
            VirtSink(f'{pulse_app_name}-internal-speaker'),
            VirtSource(f'{pulse_app_name}-internal-mic'),
            VirtSource(f'{pulse_app_name}-mic'))
        
        reroiting.init()
        reroiting.route(app_name)
        self._reroutings[app_name] = reroiting

        return f'{pulse_app_name}-mic'

    def disable_rerouting(self, app_name: str):
        if app_name not in self._reroutings:
            raise Exception(f'Application {app_name} is not rerouted')

        self._reroutings.pop(app_name).cleanup()
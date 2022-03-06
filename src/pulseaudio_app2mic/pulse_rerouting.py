import pulsectl

from typing import Union
from .app_logger import create_logger

logger = create_logger(__name__)

def _log_and_raise(msg: str):
    logger.error(msg)
    raise Exception(msg)

class VirtSink:
    def __init__(self, name: str, description: str=None):
        self.name = name
        self.description = description if description else name


class VirtSource:
    def __init__(self, name: str, description: str=None):
        self.name = name
        self.description = description if description else name


class Rerouting:
    """
    Class handles all reroutings via specified virt sinks and sources (which created by this calss too).

    Every exception thrown by this class are logged, so excpicit logging is not necessary
    """

    def __init__(self, virt_sink1: VirtSink, virt_sink2: VirtSink, virt_mic1: VirtSource, virt_mic2: VirtSource):
        self._virt_sink1 = virt_sink1
        self._virt_sink2 = virt_sink2
        self._virt_mic1 = virt_mic1
        self._virt_mic2 = virt_mic2
        self._routes = {}

    def _get_sink_by_appname(self, pulse: pulsectl.Pulse, app_name: str):
        return next(filter(lambda sink: sink.proplist.get('application.name', None) == app_name, pulse.sink_input_list()), None)

    def _unload(self, pulse: pulsectl.Pulse, entities: Union[pulsectl.PulseSinkInfo, pulsectl.PulseSourceInfo], name: str):
        entity = next(filter(lambda sink: sink.name == name, entities), None)
        if entity is None:
            logger.warn(f'Object with name {name} not found. Already unloaded?')
            return
        
        try:
            pulse.module_unload(entity.owner_module)
            logger.info(f'Module {name} unloaded as {entity.owner_module}')
        except Exception as exc:
            logger.error(f'Failed to unload module {name} as {entity.owner_module}: {exc}')
    
    def init(self):
        try:
            with pulsectl.Pulse() as pulse:
                pulse.module_load('module-null-sink', f'sink_name={self._virt_sink1.name} sink_properties=device.description={self._virt_sink1.description}')
                logger.info(f'Sink {self._virt_sink1.name} created')

                pulse.module_load('module-remap-source', f'source_name={self._virt_mic1.name} master={self._virt_sink1.name}.monitor source_properties=device.description={self._virt_mic1.description}')
                logger.info(f'Source {self._virt_mic1.name} created from {self._virt_sink1.name}.monitor')
                
                pulse.module_load('module-null-sink', f'sink_name={self._virt_sink2.name} sink_properties=device.description={self._virt_sink2.description}')
                logger.info(f'Sink {self._virt_sink2.name} created')
                
                pulse.module_load('module-loopback', f'source_dont_move=true sink_dont_move=true sink={self._virt_sink2.name} source={self._virt_sink1.name}.monitor')
                logger.info(f'Source {self._virt_sink1.name}.monitor routed to {self._virt_sink2.name}')
                
                pulse.module_load('module-loopback', f'sink_dont_move=true sink={self._virt_sink2.name}')
                logger.info(f'Sink {self._virt_sink2.name} loopbacked')
                
                pulse.module_load('module-remap-source', f'source_name={self._virt_mic2.name} master={self._virt_sink2.name}.monitor source_properties=device.description={self._virt_mic2.description}')
                logger.info(f'Source {self._virt_mic2.name} created from {self._virt_sink2.name}.monitor')
                
                pulse.module_load('module-loopback', f'source_dont_move=true source={self._virt_sink1.name}.monitor')
                logger.info(f'Source {self._virt_sink1.name}.monitor loopbacked')
        except Exception as exc:
            logger.error(f'Failed to initalize rerouter with virt_sink1: {self._virt_sink1} virt_sink2: {self._virt_sink2} virt_mic1: {self._virt_mic1} virt_mic2: {self._virt_mic2}')
            raise

    
    def route(self, app_name: str):
        with pulsectl.Pulse() as pulse:
            app_input_sink = self._get_sink_by_appname(pulse, app_name)
            if app_input_sink is None:
                _log_and_raise(f'No input sink with app name {app_name} found')

            virt1_sink = pulse.get_sink_by_name(self._virt_sink1.name)
            if virt1_sink is None:
                _log_and_raise(f'No app sink with name {self._virt_sink1.name} found')

            pulse.sink_input_move(app_input_sink.index, virt1_sink.index)
            logger.info(f'App {app_name} sink input {app_input_sink.index} moved to {virt1_sink.index}')

            self._routes[app_name] = app_input_sink.sink
    
    def cleanup(self):
        with pulsectl.Pulse() as pulse:
            for app_name in self._routes:
                app_input_sink = self._get_sink_by_appname(pulse, app_name)
                if app_input_sink is None:
                    continue

                try:
                    pulse.sink_input_move(app_input_sink.index, self._routes[app_name])
                    logger.info(f'App {app_name} sink input {app_input_sink.index} moved back to {self._routes[app_name]}')
                except Exception as exc:
                    logger.error(f'Failed to move app {app_name} sink input {app_input_sink.index} back to {self._routes[app_name]}: {exc}')
                    pass
            
            self._unload(pulse, pulse.sink_list(), self._virt_sink1.name)
            self._unload(pulse, pulse.sink_list(), self._virt_sink2.name)
            self._unload(pulse, pulse.source_list(), self._virt_mic1.name)
            self._unload(pulse, pulse.source_list(), self._virt_mic2.name)
import abc


class MySuperCommunicator:
    def __init__(self, plugins):
        for plugin in plugins:
            print(plugin)
            plugin.connect()

    def __del__(self, plugins):
        for plugin in plugins:
            print(plugin)
            plugin.disconnect()


class Plugin(abc.ABC):
    @abc.abstractmethod
    def connect(self): ...

    @abc.abstractmethod
    def disconnect(self): ...


class WhatsAppPlugin(Plugin):
    def connect(self): ...

    def disconnect(self): ...


class ViberPlugin(Plugin):
    def connect(self): ...

    def disconnect(self): ...


class GaduGaduPlugin(Plugin):
    def connect(self): ...

    def disconnect(self): ...


if __name__ == "__name__":
    com = MySuperCommunicator([
        WhatsAppPlugin,
        ViberPlugin,
        GaduGaduPlugin,
    ])
    com.run()

from pythia.cmd.action import Action
from pythia.engine.engine import Engine


class RunEngine(Action):
    def __init__(self):
        self.engine = Engine()

    def execute(self, callback):
        self.engine.run()

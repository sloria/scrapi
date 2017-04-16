class _Registry(object):

    registry = {}

    def register(self, harvester):
        self.registry[harvester.NAME] = harvester

    def __getitem__(self, attr):
        return self.registry[attr]

registry = _Registry()

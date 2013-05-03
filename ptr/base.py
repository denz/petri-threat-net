from .transition import bind


class Place(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s.%s[%s] object at %s>'%(self.__class__.__module__,
                                           self.__class__.__name__,
                                           self.name, id(self))

class Net(object):
    def __init__(self, *names):
        self.places = {}
        self.transitions = []
        for name in names:
            self.places[name] = Place(name)

    def __getitem__(self, name):
        return self.places[name]

    def bind(self, *args, **kwargs):
        self.transitions.append(bind(*args, **kwargs))
        return self.transitions[-1]

    def substitutions(self, marking):
        for transition in self.transitions:
            enabled = transition.enabled(marking)
            if enabled is not None:
                yield transition, dict(enabled)


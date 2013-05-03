from unittest import TestCase

from ptr import D3Net

class NetTestCase(TestCase):
    def net(self, n):
        return D3Net(*[i for i in range(n)])

class InputArcsTestCase(NetTestCase):
    def test_removal_from_inputs(self):
        print
        net = self.net(2)

        transition = net.bind('t',
                              inputs = {():[net.places[0],]},
                              outputs = {():[net.places[1],]},
                             )
        print list(transition({net.places[0]:[{}, {}]}))

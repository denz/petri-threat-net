from unittest import TestCase

from ptr import D3Net

class NetTestCase(TestCase):
    def net(self, n):
        return D3Net(*[i for i in range(n)])

class ArcsTestCase(NetTestCase):
    def test_removal_from_inputs(self):
        net = self.net(2)
        transition = net.bind('t',
                                inputs = {():[net.places[0],]},
                                outputs = {():[net.places[1],]}, 
                             )
        M0 = {net.places[0]:[{}]}
        self.assertTrue( list(transition(M0)) == [{net.places[1]: [{}], net.places[0]: []}] )

    def test_append_to_outputs(self):
        net = self.net(3)
        transition = net.bind('t',
                                inputs = {():[net.places[0],]},
                                outputs = {():[net.places[1],]}, 
                             )
        M0 = {net.places[1]: [], net.places[0]: [{}, {}], net.places[2]:[{},]}
        t1, M1 = next(net.submarkings(M0))
        self.assertTrue(M1=={net.places[0]: [{}],
                             net.places[1]: [{}],
                             net.places[2]: [{}]})
        self.assertTrue(t1 is transition)
        t2, M2 = next(net.submarkings(M1))
        self.assertTrue(M2=={net.places[0]: [],
                             net.places[1]: [{}, {}],
                             net.places[2]: [{}]})
        self.assertFalse(bool(list(net.submarkings(M2))))
        self.assertTrue(t2 is transition)

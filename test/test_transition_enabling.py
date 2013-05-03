from unittest import TestCase
from pprint import pprint

from ptr.transition import bind
from ptr.base import Net


class NetTestCase(TestCase):
    def net(self, n):
        return Net(*['p%s'%i for i in range(n)])

    def assertNone(self, value):
        self.assertTrue(value is None)

class TestInput(NetTestCase):
    ''' Transition t is said to be enabled or firable by `teta` under a
        marking if 
        1) each input place p of t has a token that
        matches l=`teta`, where l is the normal arc label from p to t;
        2) each inhibitor place p of t has no token that matches l=`teta`,
        where l is the inhibitor arc label; and 
        3) the guard condition
        of t evaluates to true according to `teta`.'''

    def test_empty_arc_labels(self):
        net = self.net(1)
        t = net.bind('trans0',
                 inputs={():(net.places['p0'],)},
                )

        self.assertTrue(dict(t.enabled({net.places['p0']:({'u':1,'p':1},)})) \
                                                     == {net.places['p0']: [{'u':1,'p':1}]})
        self.assertTrue(dict(t.enabled({net.places['p0']:({},)})) \
                                                     == {net.places['p0']:[{}]})

        net = self.net(2)
        t = net.bind('trans0',
                 inputs={():(net.places['p0'],
                             net.places['p1'],)},
                )

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}]})
        self.assertTrue(dict(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:({},)})) \
                                     == {net.places['p0']:[{}],
                                         net.places['p1']:[{}]})

        net = self.net(2)
        t = net.bind('trans0',
                 inputs={():(net.places['p0'],
                             net.places['p1'],)},
                )

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}]})
        self.assertTrue(dict(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:({},)})) \
                                     == {net.places['p0']:[{}],
                                         net.places['p1']:[{}]})

    def test_tuple_arc_labels(self):
        net = self.net(3)
        t = net.bind('trans0',
                 inputs={()         :(net.places['p0'],),
                         ('u',)     :(net.places['p1'],),
                         ('u','p')  :(net.places['p2'],),
                        },
                )

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     
                                     == {net.places['p0']: [{'u':1,}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertTrue(dict(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     
                                     == {net.places['p0']: [{}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ net.places['p0']:[],
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)}))

        self.assertNone(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:[],
                                         net.places['p2']:({'u':1,'p':1},)}))

        self.assertNone(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:[{'u':1,},],
                                         net.places['p2']:()}))

    def test_func_arc_labels(self):
        net = self.net(3)
        def label0(tokens):
            pass

        def label1(tokens, u=None):
            pass

        def label2(tokens, u=None, p=None):
            pass

        t = net.bind('trans0',
                 inputs={
                         label0:(net.places['p0'],),
                         label1:(net.places['p1'],),
                         label2:(net.places['p2'],),
                        },
                )

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertTrue(dict(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ net.places['p0']:[],
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)}))

        self.assertNone(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:[],
                                         net.places['p2']:({'u':1,'p':1},)}))

        self.assertNone(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:[{'u':1,},],
                                         net.places['p2']:()}))

    def test_guard_functions(self):
        net = self.net(3)
        def label0(tokens):
            pass

        def label1(tokens, u=None):
            pass

        def label2(tokens, u=None, p=None):
            pass

        def guard(u=None, p=None):
            return p != 2

        t = net.bind('trans0',
                 guard = guard,
                 inputs={
                         label0:(net.places['p0'],),
                         label1:(net.places['p1'],),
                         label2:(net.places['p2'],),
                        },
                )

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                    net.places['p1']:({'u':1,'p':2},),
                                    net.places['p2']:({'u':1,'p':2},)})) 

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,'p':2},),
                                    net.places['p1']:({'u':1,'p':1},),
                                    net.places['p2']:({'u':1,'p':2},)}))

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,'p':2},),
                                    net.places['p1']:({'u':1,'p':2},),
                                    net.places['p2']:({'u':1,'p':1},)}))

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,},),
                                    net.places['p1']:({'u':1,},),
                                    net.places['p2']:({'u':1,'p':2},)})) 

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,},),
                                    net.places['p1']:({'u':1,},),
                                    net.places['p2']:({'u':1,'p':2},)}))

        self.assertNone(t.enabled({ net.places['p0']:({'u':1,},),
                                    net.places['p1']:({'u':1,'p':2},),
                                    net.places['p2']:({'u':1,'p':1},)}))


        self.assertTrue(dict(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{}],
                                         net.places['p1']: [{'u':1,}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ net.places['p0']:[],
                                         net.places['p1']:({'u':1,},),
                                         net.places['p2']:({'u':1,'p':2},)}))

        self.assertNone(t.enabled({ net.places['p0']:({},),
                                         net.places['p1']:[],
                                         net.places['p2']:({'u':1,'p':1},)}))

        self.assertNone(t.enabled({ net.places['p0']:({'p':2},),
                                         net.places['p1']:[{'u':1,},],
                                         net.places['p2']:()}))

class TestInhibitor(NetTestCase):
    def test_guard_functions_with_inhibitor(self):
        net = self.net(4)
        def label0(tokens):
            pass

        def label1(tokens, u=None):
            pass

        def label2(tokens, u=None, p=None):
            pass

        def guard(u=None, p=None):
            return p != 2

        t = net.bind('trans0',
                 guard = guard,
                 inputs={
                         label0:(net.places['p0'],),
                         label1:(net.places['p1'],),
                         label2:(net.places['p2'],),
                        },
                 inhibitors = {
                            ('u', 'p'):(net.places['p3'],)
                 }
                )


        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertTrue(dict(t.enabled({ net.places['p0']:({'u':1,'p':1},),
                                         net.places['p1']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},),
                                         net.places['p2']:({'u':1,'p':1},)})) \
                                     == {net.places['p0']: [{'u':1,'p':1}],
                                         net.places['p1']: [{'u':1,'p':1}],
                                         net.places['p2']: [{'u':1,'p':1}]})

        self.assertNone(t.enabled({ 
                                    net.places['p0']:({'u':1,'p':1},),
                                    net.places['p1']:({'u':1,'p':1},),
                                    net.places['p2']:({'u':1,'p':1},),
                                    net.places['p3']:({'u':1,'p':2},)
                                  }))
# -*- coding: utf-8 -*-
from unittest import TestCase
from pprint import pprint

from ptr.transition import bind
from ptr.base import D3Net

def legal_attempt_guard(u, p):
    '''(?u,?p)'''
    return True

def illegal_attempt_guard(u, p):
    '''(?u,?p)[?u!=""]'''
    return True

def login_net():
    net = D3Net(*['p%s'%i for i in range(5)])
    net.bind('startLogin',
             inputs={():(net.places['p0'],)},
             outputs={():(net.places['p1'],)})

    net.bind('legalAttempt',
             guard = legal_attempt_guard,
             inputs={():(net.places['p1'],),
                     ('u', 'p'):(net.places['p2'],)
                    },
             outputs={():(net.places['p1'],)})

    net.bind('illegalAttempt',
             guard=illegal_attempt_guard,
             inputs={('u', 'p'):(net.places['p3'],)},
             outputs={():(net.places['p4'],)},
             inhibitors={('u1', 'p1'):(net.places['p2'],)}
            )

    net.bind('attack',
             inputs={():(net.places['p4'],)},
             is_attack=True)


    return net

class TestLogin(TestCase):
    def test_define_login_net(self):
        print
        net = login_net()
        net.render()
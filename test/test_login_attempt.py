# -*- coding: utf-8 -*-
from unittest import TestCase
from pprint import pprint

from ptr.transition import bind
from ptr.render import D3Net

def illegal_attempt_guard(u=None, p=None):
    '''(?u,?p)[?u!=""]'''
    return u != ""

def legal_attempt_to_p1_arc_label(tokens):
    return {}

def login_net():
    net = D3Net(*['p%s'%i for i in range(5)])
    net.bind('startLogin',
             inputs={():(net.places['p0'],)},
             outputs={():(net.places['p1'],)})

    net.bind('legalAttempt',
             inputs={():(net.places['p1'],),
                     ('u', 'p'):(net.places['p2'],)
                    },
             outputs={legal_attempt_to_p1_arc_label:(net.places['p1'],)})

    net.bind('illegalAttempt',
             guard=illegal_attempt_guard,
             inputs={('u', 'p'):(net.places['p3'],)},
             outputs={():(net.places['p4'],)},
             inhibitors={('u', 'p'):(net.places['p2'],)}
            )

    net.bind('attack',
             inputs={():(net.places['p4'],)},
             is_attack=True)
    return net

class TestLogin(TestCase):
    def test_define_login_net(self):
        print
        net = login_net()

        M0 = {net.places['p1']:[{},],
              net.places['p2']:[{'u':'ID1', 'p':'PSWD1'},],
              net.places['p3']:[{'u':'IDn+1', 'p':'PSWDn+1'},]
             }

        pprint (dict(net.substitutions(M0)))
        net.render(marking=M0)
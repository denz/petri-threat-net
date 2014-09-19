from pprint import pprint
from copy import deepcopy as copy
from unittest import TestCase

from ptr.transition import bind
from ptr.render import D3Net
from ptr.reachability import Graph
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




class TestGraph(TestCase):
    def net(self, n):
        return D3Net(*[i for i in range(n)])    
    
    def test_of_test(self):
        net = login_net()
        M0 = {net.places['p1']:[{},],
              net.places['p2']:[{'u':'ID1', 'p':'PSWD1'},
                                {'u':'ID2', 'p':'PSWD2'},
                                {'u':'ID3', 'p':'PSWD3'}],

              net.places['p3']:[{'u':'ID4', 'p':'PSWD4'},
                                {'u':'ID5', 'p':'PSWD5'},
                                {'u':'ID6', 'p':'PSWD6'}]
             }

        g = Graph(net, M0)
        g.render('temp')
        
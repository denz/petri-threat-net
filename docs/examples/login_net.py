from pprint import pprint
from ptr.render import D3Net

from ptr.reachability import Graph

#this is a login net described in `Automated security test generation with formal threat models.pdf`

def illegal_attempt_guard(u=None, p=None):
    '''(?u,?p)[?u!=""]'''
    #define a guard function

    #autodoc string above will be a guard text for rendered html
    return u != ""

def legal_attempt_to_p1_arc_label(tokens):
    #legal attempt label function
    
    #just return an empty token, dont care about inputs
    return {}

def example_label_function(tokens, u=None, p=None):
    #example label function
    #defines that `('u', 'p')` is a label variables
    
    #this label function selects first token but can be programmed to do anything
    return tokens[0]

#create a login net with 5 places
#(D3 prefix stands for `d3.js` visualization method)
net = D3Net(*['p%s'%i for i in range(5)])

#define transitions between places
#each `bind` call defines one transition
net.bind(
        #name of transition
        'startLogin',
        #define input arcs.
        #dictionary keys defines a label.
        
        #dictionary items defines a set of places bound with this transition as input output or inhibitor
         inputs={():(net.places['p0'],)},
        #define output arcs
         outputs={():(net.places['p1'],)})

net.bind('legalAttempt',
         inputs={():(net.places['p1'],),
                 ('u', 'p'):(net.places['p2'],)
                },
         outputs={legal_attempt_to_p1_arc_label:(net.places['p1'],)})

net.bind('illegalAttempt',
         guard=illegal_attempt_guard,
         #Label can be a tuple or function with keyword args
         inputs={('u', 'p'):(net.places['p3'],)},
         outputs={():(net.places['p4'],)},
         #define inhibitor arcs
         inhibitors={('u', 'p'):(net.places['p2'],)}
        )

net.bind('attack',
         inputs={():(net.places['p4'],)},
         #set this transition to be attack transition
         is_attack=True)    

#create initial marking
M0 = {net.places['p1']:[{},],
      net.places['p2']:[{'u':'ID1', 'p':'PSWD1'},
                        {'u':'ID2', 'p':'PSWD2'},
                        {'u':'ID3', 'p':'PSWD3'}],

      net.places['p3']:[{'u':'ID4', 'p':'PSWD4'},
                        {'u':'ID5', 'p':'PSWD5'},
                        {'u':'ID6', 'p':'PSWD6'}]
     }

#render a current net state to html
net.render(marking=M0, dir='.')

#create a reachability graph for login net and initial marking
g = Graph(net, M0)

#pretty print a list of node sequences that leads to attcaks
pprint (g.attacks)

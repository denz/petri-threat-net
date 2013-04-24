import subprocess
from inspect import getargspec
import json
from tempfile import NamedTemporaryFile as Temp
from Queue import Queue

from .transition import bind
from .template import TEMPLATE, PLACE_MARKER, ARC_MARKER, TRANSITION_NAME_MARKER, TRANSITION_GUARD_MARKER


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

class Place(object):
    def __init__(self, name):
        self.name = name

class Marking(object):
    def __init__(self, net):
        pass
'''
{
    nodes:[
        {name:'p0', class:'place'},        
        {name:'p1', class:'place'},
        {name:'startLogin', class:'transition', guard:''},
        ],
    arcs:[
        {source:0, target:2, label:'', class:'input'},
        {source:2, target:1, label:'', class:'output'},
    ],
}
'''

class D3Net(Net):
    def format_arc_label(self, label):
        return '&lt;%s&gt;'%(','.join(['?%s'%var for var in label]) if label else '&cent;')

    def enabled(self, transtion, marking):
        return False

    def tokens(self, place, marking):
        return []

    def iter_places(self, markers, marking=[]):
        for name, place in self.places.items():
            yield {'name':name,
                   'class':'place',
                   'id':id(place),
                   'tokens':self.tokens(place, marking)}
            
            markers.append(PLACE_MARKER%('marker_end_%s'%id(place), name))

    def iter_transitions(self, markers, marking=[]):
        for transition in self.transitions:
            data = {
                'name':transition.__name__,
                'class':('attack ' if transition.is_attack else '') + 'transition',
                'guard':transition.guard.__doc__ if transition.guard else '',
                'id':id(transition),
                'enabled':self.enabled(transition, marking),
            }
            print data
            yield data
            markers.append(TRANSITION_NAME_MARKER%('marker_start_%s'%id(transition), transition.__name__))
            if transition.guard:
                markers.append(TRANSITION_GUARD_MARKER%('marker_end_%s'%id(transition), transition.guard.__doc__))

    def iter_arcs(self, markers, places, transitions):
        idmap = dict(((node['id'], i) for i, node in enumerate(places+transitions)))
        stpairs = []
        for transition in self.transitions:
            for arc_label, input_places in transition.inputs.items():
                for place in input_places:
                    source = idmap[id(place)]
                    target = idmap[id(transition)]
                    label = self.format_arc_label(arc_label)
                    _id = '%s_%s'%(id(place), id(transition))
                    data = {'source':source,
                           'target':target,
                           'class':'input',
                           'curved':0,
                           'id':_id}

                    if (source, target) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))

            for arc_label, output_places in transition.outputs.items():
                for place in output_places:
                    source = idmap[id(transition)]
                    target = idmap[id(place)]

                    label = self.format_arc_label(arc_label)
                    _id = '%s_%s'%(id(transition), id(place))

                    data = {'source':source,
                           'target':target,
                           'class':'output',
                           'curved':0,
                           'id':_id}
                    
                    if (target, source) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))                       

            for arc_label, inhibitor_places in transition.inhibitors.items():
                for place in inhibitor_places:
                    label = self.format_arc_label(arc_label)
                    _id = '%s_%s'%(id(place), id(transition))                    
                    data = {'source':idmap[id(transition)],
                           'target':idmap[id(place)],
                           'class':'inhibitor',
                           'label':self.format_arc_label(arc_label),
                           'curved':0,
                           'id':_id}
                    
                    if (target, source) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))

            
    def d3_env(self, marking=[]):
        markers = []
        places = list(self.iter_places(markers, marking=marking))
        transitions = list(self.iter_transitions(markers, marking=marking))
        arcs = list(self.iter_arcs(markers, places, transitions))

        for arc in arcs:
            if arc['curved'] == 1:
                opposed_id = '_'.join(reversed(arc['id'].split('_')))
                for i, arc in enumerate(arcs):
                    if arc['id'] == opposed_id:
                        arcs[i]['curved'] = -1

        return {'graph':json.dumps({'places':places, 'transitions':transitions, 'arcs':arcs}, indent=4),
                'markers':'\n\t'.join(markers)}


    def render(self, marking=[]):
        filename = None
        with Temp(delete=False, suffix='.html') as temp:
            temp.write(TEMPLATE%self.d3_env(marking=marking))
            filename = temp.name

        subprocess.call(["chromium-browser", filename])

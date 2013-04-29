import subprocess
from inspect import getargspec
from math import sin, cos
import json
from tempfile import NamedTemporaryFile as Temp
from Queue import Queue

from .transition import bind
from .template import ( TEMPLATE,
                        PLACE_MARKER,
                        ARC_MARKER,
                        TRANSITION_NAME_MARKER,
                        TRANSITION_GUARD_MARKER,
                        PLACE_TOKENS,
                        PLACE_INFO,
                        TOKEN_INFO)


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
            yield transition.enabled(marking)

    def arc_label_tuple(self, arc_label):
        if callable(arc_label):
            if not hasattr(arc_label, 'label_tuple'):
                argspec = getargspec(arc_label)
                args = reversed(argspec.args if argspec.args is not None else [])
                defaults = argspec.defaults if argspec.defaults is not None else []
                arc_label.label_tuple = tuple(reversed([k for k,v in zip(args, defaults)]))
            return arc_label.label_tuple
        
        else:
            return arc_label

class D3Net(Net):
    def format_arc_label(self, label):
        return '&lt;%s&gt;'%(','.join(['?%s'%var for var in label]) if label else '&cent;')

    def iter_places(self, markers, marking={}):
        for name, place in self.places.items():
            tokens = marking.get(place, [])
            yield {'name':name,
                   'class':'place',
                   'id':id(place),
                   'tokens':tokens,}

            markers.append(PLACE_MARKER%('marker_end_%s'%id(place), name))
            if tokens:
                markers.append(PLACE_TOKENS%('marker_start_%s'%id(place), len(tokens)))

    def iter_transitions(self, markers, marking={}):
        for transition in self.transitions:
            enabled_tokens = transition.enabled(marking)
            if enabled_tokens is None:
                enabled_tokens = {}
            else:
                enabled_tokens = dict([(id(p), tokens) for p, tokens in enabled_tokens.items()])
            yield {
                'name':transition.__name__,
                'class':('attack ' if transition.is_attack else '')\
                        + ('enabled ' if enabled_tokens else '')\
                        + 'transition',
                'guard':transition.guard.__doc__ if transition.guard else '',
                'id':id(transition),
                'enabled':enabled_tokens,
            }
            markers.append(TRANSITION_NAME_MARKER%('marker_start_%s'%id(transition),
                                                    transition.__name__))
            if transition.guard:
                markers.append(TRANSITION_GUARD_MARKER%('marker_end_%s'%id(transition),
                                                        transition.guard.__doc__))

    def iter_arcs(self, markers, places, transitions):
        idmap = dict(((node['id'], i) for i, node in enumerate(places+transitions)))
        stpairs = []
        for transition in self.transitions:
            for arc_label, places in transition.inputs.items():
                for place in places:
                    source = idmap[id(place)]
                    target = idmap[id(transition)]

                    label = self.format_arc_label(self.arc_label_tuple(arc_label))
                    _id = '%s_%s'%(id(place), id(transition))

                    data = {'source':source,
                           'target':target,
                           'class':'input',
                           'curved':0,
                           'label':label,
                           'id':_id}

                    if (source, target) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))

            for arc_label, places in transition.outputs.items():
                for place in places:
                    source = idmap[id(transition)]
                    target = idmap[id(place)]

                    label = self.format_arc_label(self.arc_label_tuple(arc_label))
                    _id = '%s_%s'%(id(transition), id(place))

                    data = {'source':source,
                           'target':target,
                           'class':'output',
                           'curved':0,
                           'label':label,
                           'id':_id}

                    if (target, source) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))

            for arc_label, places in transition.inhibitors.items():
                for place in places:
                    source = idmap[id(transition)]
                    target = idmap[id(place)]
                    
                    label = self.format_arc_label(self.arc_label_tuple(arc_label))
                    _id = '%s_%s'%(id(place), id(transition))

                    data = {'source':source,
                           'target':target,
                           'class':'inhibitor',
                           'curved':0,
                           'label':label,
                           'id':_id}

                    if (target, source) in stpairs:
                        data['curved'] = 1
                    else:
                        stpairs.append((source, target))
                    yield data
                    markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))

    def d3_env(self, marking={}):
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

        return {'graph':json.dumps({'places':places,
                                    'transitions':transitions,
                                    'arcs':arcs}, indent=4),
                'markers':'\n\t'.join(markers),
                'tokens':self.tokens_info(marking)}

    def tokens_info(self, marking):
        infos = []
        for place, tokens in marking.items():
            if tokens:
                infos.append(PLACE_INFO%{'id':'place-text-%s'%id(place),
                                         'name':place.name,
                                         'tokens':'\n'.join((TOKEN_INFO%('token-text-%s'%id(token),
                                                                          token.__repr__()) for token in tokens))})
        return '\n'.join(infos)
    def render(self, marking={}):
        return TEMPLATE%self.d3_env(marking=marking)

    def display(self, marking={}):
        filename = None
        with Temp(delete=False, suffix='.html') as temp:
            temp.write(self.render(marking=marking))
            filename = temp.name

        subprocess.call(["chromium-browser", filename])


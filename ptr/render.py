import os
import json
from tempfile import NamedTemporaryFile as Temp
import subprocess

from .base import Net
from .transition import arc_label_tuple
from .template import ( MARKING_TEMPLATE,
                        PLACE_MARKER,
                        ARC_MARKER,
                        TRANSITION_NAME_MARKER,
                        TRANSITION_GUARD_MARKER,
                        PLACE_TOKENS,
                        PLACE_INFO,
                        TOKEN_INFO,
                        GRAPH_TEMPLATE)

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

    def arc_data(self, transition, arcdef, stpairs, idmap, markers, curved, cls, rev):
        for arc_label, places in arcdef.items():
            for place in places:
                if rev:
                    source = idmap[id(transition)]
                    target = idmap[id(place)]
                else:
                    source = idmap[id(place)]
                    target = idmap[id(transition)]


                label = self.format_arc_label(arc_label_tuple(arc_label))
                _id = '%s_%s'%(source, target)

                data = {'source':source,
                       'target':target,
                       'class':cls,
                       'curved':0,
                       'label':label,
                       'id':_id}
                if curved(source, target):
                    data['curved'] = 1
                else:
                    stpairs.append((source, target))
                yield data
                markers.append(ARC_MARKER%('marker_mid_%s'%_id, label))    
    
    def iter_arcs(self, markers, places, transitions):
        idmap = dict(((node['id'], i) for i, node in enumerate(places+transitions)))
        stpairs = []
        for transition in self.transitions:
            for arcdef, curved, cls, rev in ((transition.inputs,
                                             (lambda source, target:(source, target) in stpairs),
                                             'input',
                                             False),
                                            (transition.outputs,
                                             (lambda source, target:(target, source) in stpairs),
                                             'output',
                                             True),
                                            (transition.inhibitors,
                                             (lambda source, target:(source, target) in stpairs),
                                             'inhibitor',
                                             False)):
                for data in self.arc_data(transition, arcdef, stpairs, idmap, markers, curved, cls, rev):
                    yield data

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

    def render(self, marking={}, dir=None):
        if not os.path.exists(dir):
            os.makedirs(dir)

        for fname in os.listdir(dir):
            fpath = os.path.join(dir, fname)
            if os.path.isfile(fpath) and fpath.endswith('.html'):
                os.unlink(fpath)

        filename = None

        with Temp(delete=False, suffix='.html', dir=dir) as temp:
            temp.write(MARKING_TEMPLATE%self.d3_env(marking=marking))
            filename = temp.name

        return filename
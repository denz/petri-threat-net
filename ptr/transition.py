from copy import copy
import types
from collections import defaultdict, Iterable
from itertools import product, chain
from inspect import getargspec

def matches(label, token):
    #maybe exact match is implyed
    return set(token.keys()).issuperset(set(label))

def input_variations(marking):
    keys = []
    values = []

    for k,v in marking.items():
        keys.append(k)
        values.append(v)

    for tokens in product(*marking.values()):
        yield zip(keys, tokens)

def arc_label_tuple(arc_label):
    if callable(arc_label):
        if not hasattr(arc_label, 'label_tuple'):
            argspec = getargspec(arc_label)
            args = reversed(argspec.args if argspec.args is not None else [])
            defaults = argspec.defaults if argspec.defaults is not None else []
            arc_label.label_tuple = tuple(reversed([k for k,v in zip(args, defaults)]))
        return arc_label.label_tuple
    else:
        return arc_label

def without(marking, variation):
    for place, token in variation:
        if place in marking:
            tokens = [t for t in marking[place] if not t is token]
            yield place, tokens

def output_labeled(arclabel, tokens):
    combinations = []
    if isinstance(arclabel, Iterable):
        for token in tokens:            
            t = dict([(k, token.get(k, None)) for k in arclabel])
            if not t in combinations:
                yield t
                combinations.append(t)

    if callable(arclabel):
        token = arclabel(tokens)
        if isinstance(token, types.GeneratorType):
            for t in token:
                if not t in combinations:
                    yield t
                    combinations.append(token)
        else:
            if not token in combinations:
                yield token
                combinations.append(token)



def bind(name=None,
         guard=None,
         doc='',
         inputs={},
         outputs={},
         inhibitors={},
         is_attack=False):
    '''
    name - name of transition
    guard - guard function of transition
    inputs, outputs, inhibitors:
        dictionary of {arc_label:(Place(),...)}
            arc_label is a function that tests and transforms tokenlist
    is_attack - bool
    '''

    def split(marking):
        input_places = list(chain(*inputs.values()))
        output_places = list(chain(*outputs.values()))
        return [m for m in marking if m in input_places],\
               [m for m in marking if m in output_places], \
               [m for m in marking if not (m in input_places or m in output_places)]

    def translate(marking):
        '''
        generates a markings representing firing this transition with @marking
        '''
        if not enabled(marking):
            return
        input_places, output_places, unrelated_places = split(marking)
        input_marking = dict([(k,v) for k,v in marking.items() if k in input_places])
        output_marking = dict([(k,v) for k,v in marking.items() if k in output_places])
        neutral_marking = dict([(k,v) for k,v in marking.items() if k in unrelated_places])

        combinations = []
        for variation in input_variations(input_marking):
            sub = defaultdict(list, without(input_marking, variation))
            sub.update(neutral_marking)
            tokenstack = [v[1] for v in variation]
            for arc_label, places in outputs.items():
                for token in output_labeled(arc_label, tokenstack):
                    for place in places:
                        sub[place].extend(output_marking.get(place, []))
                        sub[place].append(token)

            sub = dict(sub)
            if not sub in combinations:
                yield sub
                combinations.append(sub)

    def enabled(marking):
        for label, places in inhibitors.items():
            for place in places:
                for token in marking.get(place, []):
                    if matches(label, token):
                        return

        tokenmap = defaultdict(list)
        for label, places in inputs.items():
            label = arc_label_tuple(label)
            placed_tokens = defaultdict(list)
            for place in places:
                for token in marking.get(place, []):
                    if matches(label, token):
                        if not guard:
                            placed_tokens[place].append(token)
                        elif bool(guard(**token)):
                            placed_tokens[place].append(token)
            if sorted(placed_tokens.keys()) != sorted(places):
                return

            for place, tokens in placed_tokens.items():
                tokenmap[place].extend(tokens)

        return tokenmap

    translate.__doc__ = doc
    translate.__name__ = name
    translate.guard = guard
    translate.is_attack = is_attack
    translate.inputs = inputs
    translate.outputs = outputs
    translate.inhibitors = inhibitors
    translate.enabled = enabled

    return translate
from copy import copy
import types
from collections import defaultdict, Iterable
from itertools import product
from inspect import getargspec

def matches(label, token):
    #maybe exact match is implyed
    return set(token.keys()).issuperset(set(label))

def variations(marking):
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
            if not token in combinations:
                yield dict([(k, token.get(k, None)) for k in arclabel])
                combinations.append(token)

    if callable(arclabel):
        token = arclabel(tokens)
        if isinstance(token, types.GeneratorType):
            for t in token:
                if not t in combinations:
                    yield t
                    combinations.append(t)
        else:
            yield t

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

    def translate(marking):
        '''
        generates a markings representing firing a transition with @marking
        
        @marking: is filtered of non enabled places and tokens for this transition
        '''
        combinations = []
        for variation in variations(marking):
            cleaned = defaultdict(list, without(marking, variation))
            tokenstack = [v[1] for v in variation]
            for arc_label, places in outputs.items():
                for token in output_labeled(arc_label, tokenstack):
                    subtokened = copy(cleaned)
                    for place in places:
                        subtokened[place].append(token)
                    result = dict(subtokened)
                    if not result in combinations:
                        yield result
                        combinations.append(result)



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
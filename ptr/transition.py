from collections import defaultdict
from itertools import product

def matches(label, token):
    #maybe exact match is implyed
    return set(token.keys()).issuperset(set(label))


def substitutions(tokenmap, inputs, result=()):    
    for tokens in product(*[tokenmap[p] for p in inputs]):
        yield zip(inputs, tokens)


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
            arc_label is a tuple of 'literals' to match again

            calling of arc_label with token returns a substitution
    is_attack - bool
    '''
    def translate(marking):
        #returns a marking representing firing a transition with incoming marking
        new_marking = {}

        for place in []:
            pass

    def substitutions(marking):
        '''
        marking:
        {place:[token, ...]}
        token:
        {'u':'ID1', 'p':'PSWD1'}

        Transition t is said to be enabled or firable by `teta` under a
        marking if:
        '''
        for label, places in inhibitors.items():
            for place in places:
                for token in marking[place]:
                    if matches(label, token):
                        return

        tokenmap = defaultdict(list)

        for label, places in inputs.items():
            placed_tokens = defaultdict(list)
            for place in places:
                for token in marking[place]:
                    if matches(label, token):
                        if guard(**token):
                            placed_tokens[place].append(token)

            if sorted(placed_tokens.keys()) != sorted(places):
                return
            
            for place, tokens in placed_tokens.items():
                tokenmap[place].extend(tokens)

        assert sorted(tokenmap) == sorted(inputs)
        for substitution in substitutions(tokenmap, inputs):
            yield substitution
            
    translate.__doc__ = doc
    translate.__name__ = name
    translate.guard = guard
    translate.is_attack = is_attack
    translate.inputs = inputs
    translate.outputs = outputs
    translate.inhibitors = inhibitors

    return translate
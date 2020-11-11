import click
import json
from collections import deque


class DFA:

    name: str
    K: list
    Sigma: list
    Delta: dict
    s: str
    F: list

    def __init__(self):
        self.save_file = 'dfa_save_file.json'

        try:
            self.load()
        except IOError:
            self.name = 'default'
            self.K = []  # list of Strings that act as States
            self.Sigma = []  # List of chars that defines the alphabet (defines valid input chars)
            self.Delta = {}  # Function that translates states and chars to new states in the form (state,char) : state
            self.s = ''  # begin state, needs to be in K
            self.F = []  # list of end-states, need to be in K
            self.save()

    def rm_state(self, state: str):
        if state in self.K:
            if self.s == state: self.s = ''
            self.F = [s for s in self.F if s != state]
            self.K = [s for s in self.K if s != state]
            self.save()

            new_delta = {}
            for state1 in self.Delta:
                for char, state2 in self.Delta[state1].items():
                    if state1 != state and state2 != state:
                        if state1 not in new_delta:
                            new_delta[state1] = {}
                        new_delta[state1][char] = state2

            self.Delta = new_delta

    def load(self):
        with open(self.save_file, 'r') as file:
            s_dict = json.load(file)

        self.name = s_dict['name']
        self.K = s_dict['K']
        self.Sigma = s_dict['Sigma']
        self.Delta = s_dict['Delta']
        self.s = s_dict['s']
        self.F = s_dict['F']

        file.close()

    def save(self):
        s_dict = {'name': self.name, 'K': self.K, 'Sigma': self.Sigma, 'Delta': self.Delta, 's': self.s, 'F': self.F}

        with open(self.save_file, 'w') as file:
            json.dump(s_dict, file, indent=4)

        file.close()

    def valid(self):
        # TODO: validate Delta
        # TODO: make sure Elements of s,F and Delta! are in K
        f_in_k = False if [f_ for f_ in self.F if f_ not in self.K] else True
        return self.K != [] and self.Sigma != [] and self.s in self.K and self.F != [] and f_in_k

    def __repr__(self):
        return f'{self.name}:\n' \
               f'K: {self.K}\n' \
               f'Σ: {self.Sigma}\n' \
               f'ẟ: {self.Delta}\n' \
               f's: {self.s}\n' \
               f'F: {self.F}\n'


dfa = DFA()


class SaveDecorator(object):

    def __init__(self, func):
        self.__name__ = func.__name__
        self.func = func

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
        dfa.save()


@click.group()
def cli():
    """this script enables you to quickly define a definite finite automaton from the command line"""
    pass


@cli.command()
def check():
    click.echo(str(dfa))


@cli.command()
@click.option('--step', is_flag=True)
@click.argument('word', type=str)
def run(word, step):
    # check if dfa is valid
    if not dfa.valid():
        raise Exception(f'DFA: {dfa.name} is not valid yet')
    # check if word is valid
    if word:    # empty word is allowed!
        for c in word:
            if c not in dfa.Sigma:
                raise Exception(f'{word} is not a valid word over Sigma = {dfa.Sigma}')

    current_state = dfa.s
    for c in word:
        new_state = dfa.Delta[current_state][c]
        if step:
            cmd = input(f'({current_state},{c}) -> {new_state}\npress any key or [q]uit... ')
            if cmd in ['q', 'quit']: break
        current_state = new_state
    click.echo(f'{word} accepted by {dfa.name}' if current_state in dfa.F else f'{word} not accepted by {dfa.name}')


# group used to configure states of automaton
@cli.group()
def k():
    """used to manipulate the states of the dfa"""
    pass


# command for overriding states in dfa
@k.command()
@click.argument('new_states', type=str)
@SaveDecorator
def set(new_states: str):
    """set command for the states variable"""
    new_states = new_states.split(',')
    new_states = [s.strip() for s in new_states]
    for state in dfa.K:
        if state not in new_states:
            dfa.rm_state(state)
    dfa.K = new_states


# command for adding states to dfa
@k.command()
@click.argument('new_states', type=str)
@SaveDecorator
def add(new_states: str):
    """add command for the states variable"""
    new_states = new_states.split(',')
    new_states = [s.strip() for s in new_states]
    dfa.K += new_states


# command for removing states in dfa
@k.command()
@click.argument('del_states', type=str)
@SaveDecorator
def rm(del_states: str):
    """remove command for the states variable"""
    del_states = del_states.split(',')
    del_states = [s.strip() for s in del_states]
    for state in dfa.K:
        if state in del_states:
            dfa.rm_state(state)


@cli.group()
def sigma():
    pass


@sigma.command()
@click.argument('alpha', type=str)
@SaveDecorator
def set(alpha):
    """set command for the Sigma variable"""
    dfa.Sigma = []
    for c in alpha:
        if c not in dfa.Sigma:
            dfa.Sigma.append(c)


@sigma.command()
@click.argument('alpha', type=str)
@SaveDecorator
def add(alpha):
    """add command for the Sigma variable"""
    for c in alpha:
        if c not in dfa.Sigma:
            dfa.Sigma.append(c)


@sigma.command()
@click.argument('alpha', type=str)
@SaveDecorator
def rm(alpha):
    """remove command for the Sigma variable"""
    temp = [c for c in dfa.Sigma if c not in alpha]
    dfa.Sigma = temp


@cli.command()
@click.argument('start_state', type=str)
@SaveDecorator
def start(start_state):
    """set command for the s variable"""
    if start_state in dfa.K:
        dfa.s = start_state
    else:
        if input(f'{start_state} does not exist. Do you want to create it?\n[y]es/[n]o: ') in ['yes', 'y']:
            dfa.K.append(start_state)
            dfa.s = start_state
    click.echo(f'start state is now {dfa.s}')


@cli.group()
def f():
    pass


@f.command()
@click.argument('final_states', type=str)
@SaveDecorator
def set(final_states):
    """set command for the F variable"""
    final_states = [s.strip() for s in final_states.split(',')]
    for fs in final_states:
        if fs not in dfa.K:
            answer = input(f'{fs} is not in K would you like to add it or skip?\n[a/y] = add / [s/n] = skip: ')
            if answer in ['yes', 'y', 'add', 'a']:
                dfa.K.append(fs)
            else: continue
        dfa.F.append(fs)


@f.command()
@click.argument('final_states', type=str)
@SaveDecorator
def add(final_states):
    """add command for the F variable"""
    final_states = [s.strip() for s in final_states.split(',')]
    for fs in final_states:
        if fs not in dfa.F:
            if fs not in dfa.K:
                answer = input(f'{fs} is not in K would you like to add it or skip?\n[a/y] = add / [s/n] = skip: ')
                if answer in ['yes', 'y', 'add', 'a']:
                    dfa.K.append(fs)
                else: continue
            dfa.F.append(fs)


@f.command()
@click.argument('final_states', type=str)
@SaveDecorator
def rm(final_states, full):
    """remove command for the F variable"""
    final_states = [s.strip() for s in final_states.split(',')]
    dfa.F = [fs for fs in dfa.F if fs not in final_states]


@cli.group()
def delta():
    pass


@delta.command()
@SaveDecorator
def build():
    state_q = deque(dfa.K)

    for state in state_q:
        if state not in dfa.Delta:
            dfa.Delta[state] = {}

        for char in dfa.Sigma:
            while char not in dfa.Delta[state]:
                res = input(f'({state},{char}) -> ')
                res.strip()

                if res in dfa.K:
                    dfa.Delta[state][char] = res

                else:
                    answer = input(f'{res} is not in K do you want to create it?\n[y]es/[n]o/[f]ront: ')
                    if answer in ['y', 'yes']:
                        dfa.K.append(res)
                        state_q.append(res)
                        dfa.Delta[state][char] = res
                    elif answer in ['f', 'front']:
                        dfa.K.append(res)
                        state_q.appendleft(res)
                        dfa.Delta[state][char] = res
                    # else: repeat loop and ask for new res


@delta.command()
@SaveDecorator
def change():
    pass

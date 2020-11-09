import click
import json


class DFA:

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
            self.K = []  # list of Strings that act as States
            self.Sigma = []  # List of chars that defines the alphabet (defines valid input chars)
            self.Delta = {}  # Function that translates states and chars to new states in the form (state,char) : state
            self.s = ''  # begin state, needs to be in K
            self.F = []  # list of end-states, need to be in K
            self.save()

    def load(self):
        with open(self.save_file, 'r') as f:
            s_dict = json.load(f)

        self.K = s_dict['K']
        self.Sigma = s_dict['Sigma']
        self.Delta = s_dict['Delta']
        self.s = s_dict['s']
        self.F = s_dict['F']

        f.close()

    def save(self):
        s_dict = {'K': self.K, 'Sigma': self.Sigma, 'Delta': self.Delta, 's': self.s, 'F': self.F}

        with open(self.save_file, 'w') as f:
            json.dump(s_dict, f)

        f.close()


dfa = DFA()


@click.group()
def cli():
    """this script enables you to quickly define a definite finite automaton from the command line"""
    pass

# group used to configure states of automaton
@cli.group()
def state():
    """used to manipulate the states of the dfa"""
    pass


# command for overriding states in dfa
@state.command()
@click.argument('new_states', type=str)
def set(new_states: str):
    """set command for the states variable"""
    new_states = new_states.split(',')
    new_states = [state.strip() for state in new_states]
    dfa.K = new_states
    dfa.save()
    click.echo(str(dfa) + ' is now ' + str(dfa.K))


# command for adding states to dfa
@state.command()
@click.argument('new_states', type=str)
def add(new_states: str):
    """add command for the states variable"""
    new_states = new_states.split(',')
    new_states = [state.strip() for state in new_states]
    dfa.K += new_states
    dfa.save()
    click.echo(str(dfa) + ' is now ' + str(dfa.K))


# command for removing states in dfa
@state.command()
@click.argument('del_states', type=str)
def rm(del_states: str):
    """remove command for the states variable"""
    del_states = del_states.split(',')
    del_states = [state.strip() for state in del_states]
    dfa.K = [state for state in dfa.K if state not in del_states]
    dfa.save()
    click.echo(str(dfa) + ' is now ' + str(dfa.K))


@cli.group()
def alphabet():
    pass


@cli.command()
@click.argument('start_state', type=str)
def start(start_state):
    if start_state in dfa.K:
        dfa.s = start_state
    else:
        if input(f'{start_state} does not exist. Do you want to create it?\n[y]es/[n]o: ') in ['yes', 'y']:
            dfa.K.append(start_state)
            dfa.s = start_state
    click.echo(f'start state is now {dfa.s}')
    dfa.save()


@cli.group()
def accept():
    pass


@cli.group()
def transition():
    pass


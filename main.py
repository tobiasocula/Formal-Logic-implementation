import numpy as np
import pandas as pd

# help function
def filter_symbols(a, b):
    # a and b are lists of symbols
    res = a[:]
    for el_b in b:
        if el_b not in res:
            res.append(el_b)

    return res

class Formula:

    def __init__(self, symb: str, func: callable=None, arity: int=1, symbols=None):
        """
        if singular function:
            only specified: symb (single letter)
        """
        self.symb = symb
        self.arity = arity

        if symbols is None:
            # singular
            self.symbols = [symb]
            self.singular = True
            def f(x):
                # assumes "symb" is an entry in the dict
                return x[symb]
            self.func = f
        else:
            # not singular
            self.symbols = symbols
            self.singular = False
            self.func = func
        

    def or_(self, other):
        assert isinstance(other, Formula), AssertionError()
        new_symbols = filter_symbols(self.symbols, other.symbols)
        new_arity = len(new_symbols)

        def new_func(x):
            # x is a dict
            assert len(x) == new_arity, AssertionError()
            self_args = {}
            other_args = {}
            for k,v in x.items():
                if k in self.symbols:
                    self_args[k] = v
                if k in other.symbols:
                    other_args[k] = v
            return self.func(self_args) or other.func(other_args)

        if self.singular and other.singular:
            new_str = f"{self.symb} | {other.symb}"
        elif self.singular:
            new_str = f"{self.symb} | ({other.symb})"
        elif other.singular:
            new_str = f"({self.symb}) | {other.symb}"
        else:
            new_str = f"({self.symb}) | ({other.symb})"
    
        return Formula(new_str, new_func, arity=new_arity, symbols=new_symbols)

    def and_(self, other):
        assert isinstance(other, Formula), AssertionError()
        new_symbols = filter_symbols(self.symbols, other.symbols)
        new_arity = len(new_symbols)

        def new_func(x):
            # x is a dict
            
            assert len(x) == new_arity, AssertionError()
            self_args = {}
            other_args = {}
            for k,v in x.items():
                if k in self.symbols:
                    self_args[k] = v
                if k in other.symbols:
                    other_args[k] = v
            return self.func(self_args) and other.func(other_args)

        if self.singular and other.singular:
            new_str = f"{self.symb} & {other.symb}"
        elif self.singular:
            new_str = f"{self.symb} & ({other.symb})"
        elif other.singular:
            new_str = f"({self.symb}) & {other.symb}"
        else:
            new_str = f"({self.symb}) & ({other.symb})"
    
        return Formula(new_str, new_func, arity=new_arity, symbols=new_symbols)
    
    def not_(self):

        if self.singular:
            new_str = f"!{self.symb}"
        else:
            new_str = f"!({self.symb})"
    
        return Formula(new_str, lambda x: not self.func(x), arity=self.arity, symbols=self.symbols)
    
    def implies(self, other):
        assert isinstance(other, Formula), AssertionError()
        new_symbols = filter_symbols(self.symbols, other.symbols)
        new_arity = len(new_symbols)

        def new_func(x):
            # x is a dict
            
            assert len(x) == new_arity, AssertionError()
            self_args = {}
            other_args = {}
            for k,v in x.items():
                if k in self.symbols:
                    self_args[k] = v
                if k in other.symbols:
                    other_args[k] = v
            a = self.func(self_args)
            b = other.func(other_args)
            if not a:
                return True
            return b

        if self.singular and other.singular:
            new_str = f"{self.symb} -> {other.symb}"
        elif self.singular:
            new_str = f"{self.symb} -> ({other.symb})"
        elif other.singular:
            new_str = f"({self.symb}) -> {other.symb}"
        else:
            new_str = f"({self.symb}) -> ({other.symb})"
    
        return Formula(new_str, new_func, arity=new_arity, symbols=new_symbols)
    
    def equiv(self, other):
        assert isinstance(other, Formula), AssertionError()
        new_symbols = filter_symbols(self.symbols, other.symbols)
        new_arity = len(new_symbols)

        def new_func(x):
            # x is a dict
            
            assert len(x) == new_arity, AssertionError()
            self_args = {}
            other_args = {}
            for k,v in x.items():
                if k in self.symbols:
                    self_args[k] = v
                if k in other.symbols:
                    other_args[k] = v
            a = self.func(self_args)
            b = other.func(other_args)
            return (a and b) or (not a and not b)

        if self.singular and other.singular:
            new_str = f"{self.symb} <-> {other.symb}"
        elif self.singular:
            new_str = f"{self.symb} <-> ({other.symb})"
        elif other.singular:
            new_str = f"({self.symb}) <-> {other.symb}"
        else:
            new_str = f"({self.symb}) <-> ({other.symb})"
    
        return Formula(new_str, new_func, arity=new_arity, symbols=new_symbols)
    
    def __str__(self):
        return self.symb
    
    def info(self):
        print(f"Arity: {self.arity}\nSymbols: {self.symbols}")
    
    def eval(self, **values):
        assert all([v in self.symbols for v in values.keys()]), AssertionError()
        return self.func(values)

    
    def table(self):
        depth = 2 ** self.arity
        T = np.zeros((depth, self.arity + 1), dtype=int)
        layer = np.zeros(self.arity)
        layer_mods = []
        for a in range(self.arity):
            layer_mods.append(2 ** a)
        for k in range(depth):
            arg_dict = {}
            for j in range(self.arity):
                if k % layer_mods[j] == 0:
                    layer[j] = 1 - layer[j]
                arg_dict[self.symbols[j]] = layer[j]

            T[k, -1] = self.eval(**arg_dict)
            T[k, :-1] = layer
        T = pd.DataFrame(T[::-1, :], columns=self.symbols + [self.symb])
        return Table(table=T, num_symbols=self.arity, symbols=self.symbols)
    
    def is_equivalent(self, other):
        assert isinstance(other, Formula), AssertionError()
        table = self.table()
        table.add_formula(other)
        a = table.get_col_i(-1).tolist()
        b = table.get_col_i(-2).tolist()
        return all([k == l for k, l in zip(a, b)])
    
    def is_tautology(self):
        table = self.table()
        a = table.get_col_i(-1).tolist()
        return all([1 == k for k in a])

class Table:
    def __init__(self, table: pd.DataFrame, num_symbols: int, symbols: list[str]):
        self.table = table
        self.num_symbols = num_symbols
        self.symbols = symbols

    def add_formula(self, formula: Formula):
        col = np.zeros(self.table.shape[0], dtype=int)
        for i in range(self.table.shape[0]):            
            num_args = self.table.values[i, :self.num_symbols]
            d = {p: n for p, n in zip(self.symbols, num_args)}
            col[i] = formula.eval(**d)
        self.table[formula.symb] = col

    def __str__(self):
        return self.table.__str__()

    def get_col_i(self, i: int):
        return self.table.values[:, i]




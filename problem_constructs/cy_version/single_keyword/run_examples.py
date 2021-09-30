
from single_keyword import welcome_fred, welcome_wilma, welcome_barney, welcome_dino

if __name__ == '__main__':
    welcome_fred()          # ok with default Cython directives
    welcome_barney()        # ok with default Cython directives
    welcome_wilma()         # needs 'always_allow_keywords' Cython directive
    welcome_dino()          # needs 'always_allow_keywords' Cython directive

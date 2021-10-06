
from type_hints_spec_wrong import get_powers, get_powers_


if __name__ == '__main__':
    my_results = get_powers_(2)
    print(f"sums are: {my_results}")

    my_results = get_powers(2)
    print(f"sums are: {my_results}")

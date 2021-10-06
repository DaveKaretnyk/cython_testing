
from type_hints_syntax_error import get_sum_bad_type_hint, get_sum_good_type_hint

if __name__ == '__main__':
    my_list = (1, 2, 3)
    my_sum = get_sum_bad_type_hint(my_list)
    print(f"sum is: {my_sum}")

    my_list2 = (4, 5, 6)
    my_sum2 = get_sum_good_type_hint(my_list2)
    print(f"sum is: {my_sum2}")

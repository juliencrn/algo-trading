#
# Some useful functions
#

def get_gross_rate(initial_value: float, final_value: float) -> float:
    '''Returns the gross rate (between -1.0 to 1.0)'''
    return (final_value - initial_value) / initial_value

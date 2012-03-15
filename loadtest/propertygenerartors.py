import random
import datetime
from datetime import date, datetime

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
NUMBERS = "0123456789"

def _rand_chars (chars, length, is_variable=None):
    ret_length = random.randint(1,length) if is_variable else length
    return ''.join(random.sample(chars, ret_length))

def _rand_date(start,end):
    """
    Takes date OR datetime!
    """
    delta = end-start
    #timedelta cannot multiply by a float so we need to construct a fraction.
    rand_denominator = random.randint(1,100)
    rand_numerator = random.randint(1,rand_denominator) #clip the range to make sure the fraction is never > 1
    new_delta = (delta*rand_numerator)/rand_denominator
    return start + new_delta

class PropertyValueGenerator():

    #We want to keep state here. Generate a random list of options once, so we can refer to it in
    #later calls (during generation of a single set of cases).
    RANDOM_OPTIONS = None

    #The function that will be used when self.getValue() is called.
    RAND_FUNC = None
    RAND_FUNC_OPTS = None

    def __init__(self, func_name, *args):
        self.RAND_FUNC = getattr(self,func_name)
        self.RAND_FUNC_OPTS = args

    def getValue(self):
        return self.RAND_FUNC(*self.RAND_FUNC_OPTS)

    def text_gen(self, length, is_variable):
        chars = ALPHA
        return _rand_chars(chars, length, is_variable)

    def alphanumeric_gen(self, length, is_variable):
        chars = "%s%s" % (ALPHA, NUMBERS)
        return _rand_chars(chars,length,is_variable)

    def numeric_gen(self, length, is_variable):
        chars = NUMBERS
        return _rand_chars(chars, length, is_variable)

    def doublenum_gen(self):
        # TODO: is hardcoding '25' the right thing here?
        return random.random() * random.randint(1,25)


    def _generate_or_assign_options(self, option_list):
        if option_list and not self.RANDOM_OPTIONS:  #Random options not initialized so make it the passed in list.
            self.RANDOM_OPTIONS = option_list
        if not option_list and not self.RANDOM_OPTIONS:
            # Generate options
            for i in range(random.randint(3,8)):
                self.RANDOM_OPTIONS.append(self.text_gen(3,False))

        return option_list if option_list else self.RANDOM_OPTIONS

    def select (self, option_list = None):
        population = self._generate_or_assign_options(option_list)
        return random.choice(population)

    def select1 (self, option_list):
        population = self._generate_or_assign_options(option_list)
        number_of_choices = random.randint(1,len(population))
        return random.sample(population, number_of_choices)

    def rand_date(self, start,end):
        return _rand_date(start,end)





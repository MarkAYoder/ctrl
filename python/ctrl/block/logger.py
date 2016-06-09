import numpy

from .. import block
import itertools

class Logger(block.Block):
    """Logger(number_of_rows, number_of_columns) implements a logger.
    """

    def __init__(self, number_of_rows = 12000, number_of_columns = 0, 
                 *vars, **kwargs):

        # reshape
        self.reshape(number_of_rows, number_of_columns)

        # auto reset
        self.auto_reset = kwargs.pop('auto_reset', False)

        super().__init__(*vars, **kwargs)

    def get(self, keys = None, exclude = ()):

        # call super
        return super().get(keys, exclude = exclude + ('data',))

    def reshape(self, number_of_rows, number_of_columns):

        self.data = numpy.zeros((number_of_rows, number_of_columns), float)
        self.reset()

    def reset(self):

        self.page = 0
        self.current = 0

    def get_current_page(self):
        return self.page

    def get_current_index(self):
        return self.page * self.data.shape[0] + self.current

    def get_log(self):

        if self.page == 0:
            return self.data[:self.current,:]

        else:
            return numpy.vstack((self.data[self.current:,:],
                                 self.data[:self.current,:]))

        # reset after read?
        if self.auto_reset:
            print('Logger::auto_reset')
            self.reset()
    
    read = get_log
        
    def write(self, *values):

        #print('values = {}'.format(values))

        # stack first
        values = numpy.hstack(values)

        # reshape?
        if self.data.shape[1] != len(values):
            # reshape log
            self.reshape(self.data.shape[0], len(values))
        
        # Log data
        self.data[self.current, :] = values

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer and increment page counter
            self.current = 0
            self.page += 1

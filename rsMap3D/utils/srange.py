#!/usr/bin/env python
#
# srange.py
#
# $Id:    $
# $URL: $
#
# Part of the "pydiffract" package
#

import sys
import numpy

__version__ = "$Revision: $"
__author__  = "Jon Z. Tischler, <tischler@aps.anl.gov>" +\
              "Christian M. Schlepuetz, <cschlep@aps.anl.gov>, " +\
              "Argonne National Laboratory"
__date__    = "$Date: $"
__id__      = "$Id: $"


class srange:
    """
    String-range class.
    
    This class provides functions to convert a string representing integers and
    ranges of integers to an object which can be iterated over all the values
    contained in the string and a list of individual values or subranges can be
    retrieved.
    
    EXAMPLE::
    
        >>> sr = srange("1,3,4-5,8-11,12-13,20")
        >>> for val in sr:
                    print("%d," % val),
        1, 3, 4, 5, 8, 9, 10, 11, 12, 13, 20,
        
    NOTE:
        String ranges can only contain integer numbers and must be strictly
        monotonically increasing. Multiple identical values are not allowed.
        
    TODO:
        The issues of the above note should be addressed to make the code more
        robust and forgiving. There is no reason one should not specify sub-
        ranges in arbitrary orders.
        
    """
    
    def __init__(self, r=''):
        """
        Initialize the srange instance.
        """
        
        if type(r) is str:
            self.r = r
#         elif type(r) is unicode:
#             self.r = r.encode()
        elif type(r) is int:
            self.r = str(r)
        elif type(r) is list:
            self.list_to_srange(r)
        elif type(r) is numpy.ndarray:
            self.list_to_srange(r)
        else:
            raise TypeError("String list must be a string or (list of) integers.")
            return None
        if self.r.lower() == 'none':
            self.r = ''
        self.l = []
        self.last_item = 0

        self.reset_last()
        self.l = self._range_to_tuple_list()
        if not self._tuple_list_is_monotonic():
            raise ValueError("String range must be monotonically increasing.")
            return None
        self._compact()
    
    def __iter__(self):
        """ The class iterator """
        return self
        
    def __repr__(self):
        """ Return string representation for srange."""
        
        return "srange('%s')" % self.r
        
    def __str__(self):
        """ Return string value for srange."""
        
        return "'%s'" % self.r
        
    def __getitem__(self, n):
        """ Return the n-th element in the string range"""
        
        return self.index(n)

    def next(self):
        """ Return the next value in the string range."""
        
        if not self.l:
            raise StopIteration
        for (lo, hi) in self.l:
            if self.last_item < lo:
                self.last_item = lo
                return lo
            elif self.last_item >= lo and self.last_item < hi:
                self.last_item += 1
                return self.last_item
        self.reset_last()
        raise StopIteration

    def after(self, val):
        """
        Return the value or the element that follows after the given value.
        
        EXAMPLE::
        
            >>> sr = srange("3,5,9-20")
            >>> print sr.after(5)
            9
        
        """
        
        if not self.l:
            return None

        last_save = self.last_item
        self.last_item = val
        try:
            after = self.next()
        except:
            after = None
        self.last_item = last_save
        return after

    def first(self):
        """ Return the number of the first item in the range.
        
        EXAMPLE::
        
            >>> sr = srange("3,5,9-20")
            >>> print sr.first()
            3
            
        """
        
        if not self.l:
            raise ValueError("String range is empty.")
        l0 = self.l[0]
        return l0[0]

    def last(self):
        """ Return the number of the last item in the range.
        
        EXAMPLE::
        
            >>> sr = srange("3,5,9-20")
            >>> print sr.last()
            20
            
        """
        if not self.l:
            raise ValueError("String range is empty.")
        l1 = self.l[-1]
        return l1[1]

    def len(self):
        """Return the number of items in the string range.
        
        EXAMPLE::
        
            >>> sr = srange("3,5,9-20")
            >>> print sr.len()
            14
            
        """

        if not self.l:
            return 0

        total = 0
        for (lo, hi) in self.l:
            total += hi - lo + 1
        return total

    def is_in_range(self, item):
        """
        Return True if item is in string range self.r, False otherwise.
        """
        
        if not self.l:
            return False
        if not (type(item) is int or type(item) is int):
            raise TypeError("Element must be integer number")
            
        for (lo, hi) in self.l:
            if lo <= item and item <= hi:
                return True
        return False

    def index(self, n):
        """
        Return the n-th element from the string range.
        """
        
        if not self.l:
            raise ValueError("String range is empty.")
        if not (type(n) is int or type(n) is int):
            raise TypeError("Element must be integer number")
        if (n < 0):
            raise ValueError("Index must be non-negative.")
        if (n >= self.len()):
            raise ValueError("String range index out of range.")
    
        count = 0
        for (lo, hi) in self.l:
            end_point = count + hi-lo
            if n <= end_point:
                return (lo + n - count)
            count = end_point + 1
        return None

    def val2index(self, val):
        """ Return the index into the range string that corresponds to val.
        
        EXAMPLE::
        
            >>> r = '3, 5, 9-20'
            >>> print val2index(5)
            1
        
        """
        
        if not self.l:
            raise ValueError("String range is empty.")
        if not (type(val) is int or type(val) is int):
            raise TypeError("Value must be an integer.")
            
        index = 0
        for (lo, hi) in self.l:
            if lo <= val and val <= hi:
                return index + val - lo
            index += hi - lo + 1
        return None

    def sub_range(self, start, n, set_last=False):
        """
        Return a sub range from the original range as a new range string.
        
        The new range starts at value start and has up to n elements. If start
        is not an element in the range, then begin with first element after
        start. If set_last is True, then self.last_item is set to the new end,
        otherwise no change is made.

        EXAMPLE::
        
            >>> sr = srange('3,5,9-20')
            >>> print sr.sub_range(start = 5, n = 3)
            5,9-10
            
        """

        if not self.l:
            raise ValueError("String range is empty.")
        if not (type(start) is int or type(start) is int):
            raise TypeError("Start value (start) must be an integer.")

        if not (type(n) is int or type(n) is int):
            raise TypeError("Number of elements (n) must be an integer.")
        if n < 0:
            raise ValueError("Number of elements must be greater zero.")

        hi_new = self.last()
        lout = []
        for (lo, hi) in self.l:
            if hi < start:
                continue
            lo_new = max(lo, start)
            hi_new = min(hi, lo_new+n-1)
            n -= hi_new - lo_new + 1
            lout.append((lo_new,hi_new))
            if n < 1:
                break
                
        if set_last:
            self.last_item = hi_new
        return self._tuple_list_to_str(lout)

    def list(self):
        """
        Expand a string range into a standard list.
        
        EXAMPLE::
        
            >>> print srange("3,5,9-13").list()
            [3, 5, 9, 10, 11, 12, 13]
        
        CAUTION:
        
            The following statement::

                >>> list("1-100000",";")
            
            will produce a list with 100000 elements!
        
        """
        
        if self.len() > 10000000:
            raise IndexError("Resulting list too large.")
        if not self.l:
            return []
            
        lout = []
        for (lo, hi) in self.l:
            lout.extend(range(lo,hi+1))
        return lout

    def list_to_srange(self, input_list):
        """
        Convert a list to a string range.
        
        EXAMPLE::
        
            >>> mylist = [3,5,9,10,11,12]
            >>> sr = srange('')
            >>> sr.list_to_srange(mylist)
            >>> prints sr
            '3,5,9-12'
            
        """
        
        if not all(isinstance(n, int) for n in input_list):
            raise ValueError("List elements must be integers.")
        
        new_tuple_list = []
        for item in input_list:
            new_tuple_list.append((item,item))
        self.l = new_tuple_list
        self._compact()
        
        
    def reset_last(self):
        """ Reset last_item to the lowest possible value."""
        
        self.last_item = -sys.maxsize-1

    def _compact(self):
        """
        Return the most compact way of describing a string range.
        
        EXAMPLE::
        
            >>> sr = srange('1,2-3,4,6')
            >>> sr._compact()
            >>> print sr
            '1-4,6'
            
        NOTE:
            Compacting is done automatically during initialization.
            
        """
        
        if not self.l:
            return
        
        (last_lo, last_hi) = self.l[0]
        lnew = []
        for (lo, hi) in self.l:
            if lo > last_hi + 1:
                lnew.append((last_lo, last_hi))
                last_lo = lo
            last_hi = hi
        lnew.append((last_lo,last_hi))
        self.l = lnew
        self.r = self._tuple_list_to_str(self.l)

    def _range_to_tuple_list(self):
        """
        Convert a string range to a list of simple ranges (tuples).

        """

        if not self.r:
            return []
            
        if self.r.find('@') > 0:
            raise ValueError("Invalid character ('@') in string range.")

        l = []
        singles = self.r.split(',')
        for single in singles:
            s = single.lstrip()
            
            # A '-' after the first character indicates a contiguous range
            # If it is first character, it means a negative number
            # If no '-' is found, mid and hi will be empty strings
            i = s[1:].find('-') + 1
            if i > 0:
                s = s[0:i] + '@' + s[i+1:]
            lo,mid,hi = s.partition('@')
            lo = lo.strip()
            if lo.lower().find('-inf') >= 0:
                lo = -sys.maxsize
            elif lo.lower().find('inf') >= 0:
                lo = sys.maxsize
            try:
                lo = int(lo)
            except:
                raise ValueError("Values in string range must be integers.")
                
            if(hi):
                hi = hi.strip()
                if hi.lower().find('-inf') >= 0:
                    hi = -sys.maxsize
                elif hi.lower().find('inf') >= 0:
                    hi = sys.maxsize
                try:    
                    hi = int(hi)
                except:
                    raise ValueError("Values in string range must be integer.")            
            else:
                hi = lo

            l.append((lo, hi))
            
        return l

    def _tuple_list_is_monotonic(self):
        """
        Return True if the tuple list self.l is monotonic, False otherwise.
        
        """
        
        last_hi = None
        for (lo, hi) in self.l:
            if hi < lo:
                return False
            if last_hi:
                if last_hi >= lo:
                    return False
            last_hi = hi
        return True

    def _tuple_list_to_str(self,l):
        """
        Convert a list of tuples to a string range.
        
        EXAMPLE::
        
            >>> print _tuple_list_to_str([(1,4),(6,6)])
            '1-4,6'
            
        """

        if not l:
            return ''

        (last_lo, last_hi) = l[0]
        range_string = ''
        for (lo, hi) in l:
            if lo > last_hi + 1:
                # not a continuation, save to r
                if range_string:
                    # add this single range to r
                    range_string += ','     
                range_string += str(last_lo)
                if last_hi > last_lo:
                    range_string += '-' + str(last_hi)
                last_lo = lo
            last_hi = hi
        # add the last single range to the range_string
        if range_string:
            range_string += ','             
        range_string += str(last_lo)
        if last_hi > last_lo:
            range_string += '-'+str(last_hi)
            
        return range_string


if __name__ == "__main__":
    """
    Main function for srange.py.
    
    Test cases for srange class to verify correct behavior.
    
    """

    def test(test_str):
        """
        Test function for the srange class.
        """
        print ('\n---------------------------------------------')
        if type(test_str) is str:
            print ("The test string: '%s'" % test_str)
        else:
            print ("The test string: %s" % test_str)
            
        try:
            sr = srange(test_str)
            mystr = ''
            for val in sr:
                mystr += str(val) + ', '
            print ('Elements in str1: ', mystr)
            print ('Python list of elements in str1:', sr.list())
            print ('Number of elements in string range:', sr.len())
            print ('First element:',    sr.first())
            print ('Last element:',    sr.last())
            print ('Next element after 5:',    sr.after(5))
            print ('Next element after 16:',    sr.after(16))
            print ('Test if 5 is in range:',    sr.is_in_range(6))
            print ('Test if 6 is in range:',    sr.is_in_range(10))
            print ('Subrange from -1 with 100 elements: ', sr.sub_range(-1,100))
            print ('Subrange from 3 with 5 elements: ', sr.sub_range(3,5))
            print ('Index of 5 in string range:', sr.val2index(5))
            print ('Value at index 3 in string range:', sr.index(3))
            print ('String representation:', repr(sr))
            print ('String value:', str(sr))
            
            return sr
            
        except Exception as err:
            print ('This test returned an ERROR!')
            print (err)
            
    
    str1 = '1,3,4-5,8-11,12-13,20'         # a standard string range
    str2 = '1, 3,    4-5,8 - 11, 12-13,20' # test for dealing with whitespace
    str3 = '2,1,3'                         # illegal, since non-monotonic
    str4 = '5'                             # string range with single element
    str5 = ''                              # empty string
    str6 = 3.65                            # illegal type (should be str)
    str7 = '3.65'                          # illegal value (should be integer)
    str8 = '-3-3, 5-11'                    # negative values
    str9 = [3, 5, 9, 10, 11, 12]           # a list as input
    str10 = [3.141, 6.282, 21.063]         # illegal, list of non-integers
    str11 = numpy.array([3,5,9,10,11,12])  # numpy array instead of the list
    
    sr = test(str1)
    sr = test(str2)
    sr = test(str3)
    sr = test(str4)
    sr = test(str5)
    sr = test(str6)
    sr = test(str7)
    sr = test(str8)
    sr = test(str9)
    sr = test(str10)
    sr = test(str11) 
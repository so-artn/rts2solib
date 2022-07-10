from . import rts2_wwwapi
import json


class filter_set:


    """Class to simplify look up of filter by name and number
    

    uses the python [] operator to lookup filter number
    or name. If you give it the name it will return the 
    number and vice versa. it also uses aliases for the
    lookup. RTS2 and the Galil like to use long names
    like "Harris-U" observers like short names like "U"
    either format is acceptable as long as the alias 
    is in the dictionary below. 
    """

    # Filter Name Aliases. 
    # The keyword is the name of the filter as told by 
    # the galil and RTS2, the value in the dict is a tupple
    # of possible aliases for each filter
    # TODO read this from config
    alias = {
            "Bessell-U": ("U", 'bessell-u'),
            # "Harris-U": ("U"), 
            "Harris-R": ("R", "harris-r"), 
            "Harris-V": ("V","harris-v" ), 
            "Arizona-I": ("I",), 
            "Harris-B": ("B",),
            "Schott-8612": ("Schott",),
            "OPEN": ("Open", "open", "OPEN", "Clear", "CLEAR", "clear"),
            "Halpha": ("Halpha", "halpha")}


    def __init__( self, filters=None, prx=None ):
        """I believe that filters and prx should always be None.
        That is to say, we will read the filter list from rts2_wwwapi"""

        if filters is None:
            if prx is None:

               self._filter_list = rts2_wwwapi.rts2comm().get_filters()

        elif type(filters) == list:
            self._filter_list = filters

        elif type(filters) == dict:
            raise TypeError("Filters are should not be a dict, it probably should be None")
            # this assumes that the keywords of the dictionary are 
            # the fitler names and the value is the filter number. 


            #sort by filter number and reverse look up. 
            # this doesn't work in python3
            #for key, value in sorted(filters.iteritems(), key=lambda (k,v): (v,k)):
                #self._filter_list.append( key )

        elif type(filters) == str or type(filters) == unicode:
            self._filter_list = str(filters).split()

        else:
            raise TypeError("Unexpected filter type {}, type must be string, unicode, list or dict".format(type(filters)))


    def check_alias( self, alias ):

        for name, aliases in self.alias.items():
            if alias == name and name in self._filter_list:
                return name

            else:
                for al in aliases:
                    if al == alias and name in self._filter_list:
                        return name

        # we didn't find the alias
        return None

    def filter_flat_order(self, evening=True):
        loaded_filters = self._filter_list
        
        loaded_filters_true = [self.check_alias(lf) for lf in loaded_filters]

        filter_priority = {
            "Halpha":1,
            "Bessell-U":2,
            "Harris-B":3,
            "Harris-V":4,
            "Harris-R":5,
            "Arizona-I":6,
            "Schott-8612":7,
            "Open":8
        }

        filter_priority = dict(sorted(filter_priority.items(), key=lambda item: item[1], reverse=(not evening)))

        sorted_filters = []

        for filt in filter_priority.keys():
            temp = self.check_alias(filt)
            if temp is not None and temp in loaded_filters_true:
                sorted_filters.append(temp)

        return sorted_filters

    def __str__(self):
        return "<filter_set: "+str(self._filter_list)+">"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        if type(key) == int:
            return self._filter_list[key]

        elif type(key) == str or type(key) == unicode:
            realname = self.check_alias(key)
            if realname is not None:
                return self._filter_list.index(realname)
        raise ValueError( "cannot find filter {}".format(key) )
        

    def __contains__(self, item):
        try:
            val=self.__getitem__(item)
        except ValueError:
            return False

        return True


from typing import Counter
from app import indices, recursive_searchers
import string 

class Storage:

    def __init__(self):
        self.index = indices.Index()
        self.master = []
        self.counter = 0

    def write(self, input):
        input['id'] = self.counter
        self.master.append(input)
        
        # process indices
        self.index.process(input)
        

        self.counter = self.counter + 1
            
        return input

    def read(self, query):
        broken_down = query.split()
        operation = broken_down[1].lower()
        attribute = broken_down[0]
        value = query.strip()[len(attribute) + 1 + len(operation):].strip().lower()

        matching_apps = self.__getattribute__(operation)(attribute, value)

        # print('MATCHING APPS ARE ' + str(matching_apps))
        return [self.master[i] for i in matching_apps]


    def equals(self, attribute, value):
        index_exists = attribute + "_equals" in self.index.INDEXED_ATTRS
        order_exists = attribute + "_order" in self.index.INDEXED_ATTRS

        if index_exists:
            try:
                matches = self.index.__getattribute__(attribute.replace(".", "_") + "_equals_index")[value]
                return self.index.__getattribute__(attribute.replace(".", "_") + "_equals_index")[value]
            except KeyError as k:
                # no matches found in the index for that value
                return []
        
        elif order_exists:
            order = self.index.__getattribute__(attribute.replace(".", "_") + "_order")
            location = self.index.get_ordered_index(attribute, value)
            if location >= 0 and location < len(order):
                return [order[location][1]]
            else: 
                return [] 

        else:
            matches = []
            for app in self.master:
                matches.extend(recursive_searchers.recursive_equals(app, attribute.split("."), value, app['id']))

            return matches
        
        
    def not_equals(self, attribute, value):
        equals_set = self.equals(attribute, value)

        result = set([])

        for i in range(self.counter):
            if i not in equals_set:
                result.add(i)

        return result

    def greater_than(self, attribute, value):
       leq_set = self.less_than_or_equal(attribute, value)
       result = set([])
       
       for i in range(self.counter):
            if i not in leq_set:
                result.add(i)

       return result        
    
    def greater_than_or_equal(self, attribute, value):
        index_exists = attribute + "_order" in self.index.INDEXED_ATTRS

        if index_exists:
            order = self.index.__getattribute__(attribute.replace(".", "_") + "_order")
            location = self.index.get_ordered_index(attribute, value)
            if location >= 0:
                matches = [item[1] for item in order[location:]] # all "orders" would have (value, appID) to be compatible w other functions
                return matches
            else: 
                return [] # don't have to worry about being OOB -- python handles that for us

        else:
            matches = []
            for app in self.master:
                matches.extend(recursive_searchers.recursive_greater_than_equal_to(app, attribute.split("."), value, app['id']))
        
        return matches
    

    def less_than(self, attribute, value):
       geq_set = self.greater_than_or_equal(attribute, value)
       result = set([])
       
       for i in range(self.counter):
            if i not in geq_set:
                result.add(i)

       return result
    
    def less_than_or_equal(self, attribute, value):
        index_exists = attribute + "_order" in self.index.INDEXED_ATTRS

        if index_exists:
            order = self.index.__getattribute__(attribute.replace(".", "_") + "_order")
            location = self.index.get_ordered_index(attribute, value)
            if location >= 0:
                matches = [item[1] for item in order[:location+1]] # all "orders" would have (value, appID) to be compatible w other functions
                return matches
            else:
                return [] # don't have to worry about being OOB -- python handles that for us

        else:
            matches = []
            for app in self.master:
                matches.extend(recursive_searchers.recursive_less_than_equal_to(app, attribute.split("."), value, app['id']))
        
        return matches
    
    def contains(self, attribute, value):
        index_exists = attribute + "_contains_index" in self.index.INDEXED_ATTRS

        words = value.split()

        matches = []

        if index_exists: 
            for word in words:
                try:
                    matches.extend(self.index.__getattribute__(attribute + "_contains_index"))[word]
                except KeyError:
                    # nothing to do, missing word detected
                    pass
                
        
        else:
            for app in self.master:
                matches.extend(recursive_searchers.recursive_contains(app, attribute.split("."), value, app['id']))
        
        return matches

    def not_contains(self, attribute, value):
       contains_set = self.contains(attribute, value)
       result = set([])
       
       for i in range(self.counter):
            if i not in contains_set:
                result.add(i)

       return result



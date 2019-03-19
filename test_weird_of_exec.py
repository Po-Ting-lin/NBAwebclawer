class test(object):
    def __init__(self):
        self.proper1 = 1

    def call_it(self):
        self.proper1 += 1
        return self.proper1

    def call_it_many(self, inpu):
        for i in [1,2,3,4,5,6]:
            exec("self.proper1 +=" + str(i))
        for i in [1,2,3,4,5,6]:
            exec("inpu +=" + str(i))
        return self.proper1, inpu
    def call_it_many_input(self, inpu_n):
        inpu_n += 1
        inpu_n += 2
        inpu_n += 3
        inpu_n += 4
        inpu_n += 5
        inpu_n += 6
        return inpu_n

def call_it_in_function(ans):
    for i in [1, 2, 3, 4, 5, 6]:
        exec("ans +=" + str(i))
    return ans


# test1
obj1 = test()
obj2 = test()
print('call it', obj1.call_it())
print('call it many', obj2.call_it_many(1)[0])
print('call it many and input', obj2.call_it_many(1)[1])
print('call it many input', obj2.call_it_many_input(1))
# test2
print('call function', call_it_in_function(1))

conclusion = '''only if we exec the property of object, or exec cannot work'''
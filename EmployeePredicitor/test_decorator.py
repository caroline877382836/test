
def log(func):
    def _print(a,b):
        print "log_1"
        return func(a,b)
    return _print

@log   
def func1(a,b):
    return a + b

if  __name__ == "__main__" :
    func1(1,2)
    
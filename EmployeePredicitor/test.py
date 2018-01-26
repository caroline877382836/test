import importlib
from ctypes import cdll
#itertools = importlib.import_module("D:\TestData\FileIO.lib")

from ctypes import *
mylib = CDLL("D:\TestData\FileIO.lib")

#===============================================================================
# extern "C" {
#     Foo* Foo_new(){ return new Foo(); }
#     void Foo_bar(Foo* foo){ foo->bar(); }
# }
# 
# g++ -c -fPIC foo.cpp -o foo.o
# g++ -shared -Wl,-soname,libfoo.so -o libfoo.so  foo.o
#===============================================================================


lib = cdll.LoadLibrary('./libfoo.so')

class Foo(object):
    def __init__(self):
        self.obj = lib.Foo_new()

    def bar(self):
        lib.Foo_bar(self.obj)
        
if __name__ == "__main__" :         
    f = Foo()
    f.bar() #and you will see "Hello" on the screen
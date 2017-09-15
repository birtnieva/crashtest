from pth import *

class a(thrd):
    def __init__(self,thrid):
        thrd.__init__(self,thrid)
        self.x = None
        self.y = None
        self.z = None
        self.num = int(self.id[1])
    def run(self):
        print(self.id, 'starts')
        self.x = 5+self.num
        self.y = 12+self.num
        print(self.id, 'x:', self.x)
        print(self.id, 'pauses')
        yield '1','pause' # state in Run state
        self.z = self.x + self.y
        print(self.id, 'z:', self.z)
        print(self.id, 'waits for b-ev')
        yield '2','wait','b-ev' # enter Sleep state, waiting for the
                                # event named 'b-ev'
        print(self.id, 'z:', self.z)
        if self.id == 'a1':
            print('a1 sets a1-ev for all')
            yield '2a','set_all','a1-ev'    # wake up all threads waiting for
                                            # the event 'a1-ev'
        print(self.id, 'quits')
        yield '3','quit' # thread exits

class b(thrd):
    def __init__(self,thrid):
        thrd.__init__(self,thrid)
        self.u = None
        self.v = None
    def run(self):
        print('b starts')
        self.u = 5
        print('b pauses')
        yield '11','pause' # stay in Run state
        self.v = 8
        print('b.v:', self.v)
        print('b sets b-ev')
        yield '12','set','b-ev' # wake just one thread waiting for 'b-ev'
        print('b sets b-ev but stays')
        yield 'uv','set_but_stay','b-ev' # wake a thread but do NOT pause
        print('b quits')
        yield 'our last one','quit' # exit

class c(thrd):
    def __init__(self,thrid):
        thrd.__init__(self,thrid)
    def run(self):
        print(self.id, 'starts')
        print(self.id, 'waits for a1-ev')
        yield 'cwait','wait','a1-ev' # wate for 'a1-ev'
        print(self.id, 'quits')
        thrd.prevs(self)
        yield 'cquit','quit' # exit

def main():
    # the next few lines create a bunch of threads
    ta1 = a('a1')
    ta2 = a('a2')
    tb = b('b')
    tc1 = c('c1')
    tc2 = c('c2')
    thrd.tmgr() # start the threads manager, so threads begin

if __name__ == '__main__': main()
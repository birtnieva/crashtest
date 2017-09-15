# pth.py: non-preemptive threads for Python; inspired by the GNU PTH
# package for C/C++

# typical application will have one class for each type of thread; its
# main() will set up the threads as instances of the classes, and lastly
# will call thrd.tmgr()

# each thread type is a subclass of the class thrd; in that subclass,
# the user must override thrd.run(), with the code consisting of the
# actions the thread will take

# threads actions are triggered by the Python yield construct, in the
# following format:

# yield yieldID, action_string [, arguments]

# the yieldID is for application code debugging purposes

# possible actions:

# yield yieldID, 'pause':
# thread relinquishes this turn, rejoins runnable list at the end

# yield yieldID, 'wait', eventID:
# thread changes state to 'waiting', joins end of queue for
# the given event

# yield yieldID, 'set', eventID:
# thread sets the given event, rejoins runnable list at the end;
# the thread, if any, at head of queue for this event is inserted
# at the head of the runnable list

# yield yieldID, 'set_but_stay', eventID:
# thread sets the given event, but remains at head of runnable list;
# thread, if any, at head of queue for the event is inserted in
# runnable list following the head

# yield yieldID, 'set_all', eventID:
# thread sets the given event, rejoins runnable list at the end;
# all threads in queue for the event are inserted at the head of
# the runnable list, in the same order they had in the queue

# yield yieldID, 'quit':
# thread exits

class thrd:

    runlst = []     # runnable thread list
    evnts = {}      # a key is an event ID, a string; value is a list of
                    # threads waiting for that event
    waitlst = []    # waiting thread list
    didyield = None # thread that last performed a yield op; for
                    # application code debugging purposes

    def __init__(self,id):
        self.id = id            # user-supplied string
        self.state = 'runnable' # the other possible state is 'waiting'
        self.yieldact = ''      # action at last yield; for application code
        # debugging purposes
        self.waitevnt = ''      # what event this thread is waiting for, if any;
        # for application code debugging purposes
        self.itr = self.run()   # this thread's iterator
        thrd.runlst.append(self)

    def run(self): # stub, must override
        pass

    # triggered by: yield yieldID, 'pause'
    def do_pause(self,yv):
        del thrd.runlst[0]
        thrd.runlst.append(self)

    # triggered by: yield yieldID, 'wait', eventID
    def do_wait(self,yv):
        del thrd.runlst[0]
        self.state = 'waiting'
        self.waitevnt = yv[2]
        # check to see if this is a new event
        if yv[2] not in thrd.evnts.keys():
            thrd.evnts[yv[2]] = [self]
        else:
            thrd.evnts[yv[2]].append(self)
        thrd.waitlst.append(self)

    # reactivate first thread waiting for this event, and place it at
    # position pos of runlst
    def react(ev,pos):
        thr = thrd.evnts[ev].pop(0)
        thr.state = 'runnable'
        thr.waitevnt = ''
        thrd.waitlst.remove(thr)
        thrd.runlst.insert(pos,thr)
    react = staticmethod(react)

    # triggered by: yield yieldID, 'set', eventID
    def do_set(thr,yv):
        del thrd.runlst[0]
        thrd.runlst.append(thr)
        thrd.react(yv[2],0)
    do_set = staticmethod(do_set)

    # triggered by: yield yieldID, 'set_but_stay'
    def do_set_but_stay(thr,yv):
        thrd.react(yv[2],1)
    do_set_but_stay = staticmethod(do_set_but_stay)

    # triggered by: yield yieldID, 'set_all', eventID
    def do_set_all(self,yv):
        del thrd.runlst[0]
        ev = yv[2]
        for i in range(len(thrd.evnts[ev])):
            thrd.react(ev,i)
        thrd.runlst.append(self)

    # triggered by: yield yieldID, 'quit'
    def do_quit(self,yv):
        del thrd.runlst[0]

    # for application code debugging
    # prints info about a thread
    def prthr(self):
        print('ID: %s, state: %s, ev: %s, yldact: %s' % \
            (self.id, self.state, self.waitevnt, self.yieldact))

    # for application code debugging
    # print info on all threads
    def prthrs():
        print('runlst:')
        for t in thrd.runlst:
            t.prthr()
        print('waiting list:')
        for t in thrd.waitlst:
            thrd.prthr(t)
    prthrs = staticmethod(prthrs)

    # for application code debugging
    # printf info on all events
    def prevs(self):
        print('events:')
        for eid in thrd.evnts.keys():
            print('%s:' % eid)
            for thr in thrd.evnts[eid]:
                print(thr.id)
            print()
        prevs = staticmethod(self.prevs)

    # threads manager
    def tmgr():
        # while still have runnable threads, cycle repeatedly through them
        while (thrd.runlst):
            # get next thread
            thr = thrd.runlst[0]
            # call it
            yieldvalue = next(thr.itr)
            # the above call to next() runs the thread until a yield, with
            # the latter returning yieldvalue
            thr.yieldID = yieldvalue[0]
            thrd.didyield = thr
            # call the function requested in the yield
            yv1 = yieldvalue[1] # requested action
            thr.yieldact = yv1
            actftn = eval('thrd.do_'+yv1)
            actftn(thr,yieldvalue)
    tmgr = staticmethod(tmgr)
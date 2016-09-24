# pyRBT

Red-Black Tree (RBT) for Python2 and Python3. 
Insertion, deletion, search and retrieval in `O(log N)` time with `O(N)` space.

[![Build Status](https://travis-ci.org/noporpoise/pyRBT.svg?branch=master)](https://travis-ci.org/noporpoise/pyRBT)

Examples:

    import pyRBT
    
    rbt = pyRBT.pyRBT()
    
    # Add elements
    rbt.insert(3)
    rbt.extend([2,1,5,10])
    
    # Remove an element
    rbt.remove(3)
    
    # Remove by index
    del(rbt[0])
    
    # Test membership
    if 2 in rbt:
      print("2 in RBT!")                        # prints "2 in RBT!"
    
    # Fetch using an index
    print(rbt[1])                               # prints "5"
    
    # Iterate forwards
    print(','.join([str(v) in rbt]))            # prints "2,5,10"
    
    # Iterate backwards
    print(','.join([str(v) in reversed(rbt)]))  # prints "10,5,2"
    
    # Get number of members
    print(len(rbt))                             # prints "3"

It is also possible to use as a multiset (set containing duplicate values) if
you insert using `insert(value,True)`.

    import pyRBT
    rbt = pyRBT.pyRBT()
    rbt.insert(2)       # 2
    rbt.insert(2)       # 2
    rbt.insert(2,True)  # 2,2
    rbt.insert(1,True)  # 1,2,2
    rbt.insert(1,True)  # 1,1,2,2
    rbt.remove(1)       # remove a '1': 1,2,2
    rbt.remove(2)       # remove a '2': 1,2
    print(','.join([str(v) for v in rbt])) # print "1,2"

Run tests with:

    python2 pyRBT.py

For more on RBTs see:

* https://en.wikipedia.org/wiki/Red%E2%80%93black_tree

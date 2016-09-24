from __future__ import print_function

# https://en.wikipedia.org/wiki/Red%E2%80%93black_tree
# Invariants:
# 1. A node is either red or black.
# 2. The root is black.
# 3. All leaves are black.
# 4. If a node is red, then both its children are black.
# 5. Every path from a given node to a leaf node has the same no. of black nodes.
# Results in:
# 6. Longest root->leaf path is no more than twice as long as shortest root->leaf
#    (i.e. roughly balanced)
#
# Black depth of the tree is the number of back nodes from root to any leaf
# Longest path is 2*B-1 nodes where B is the black depth of the tree
# Shortest path is B nodes

class pyRBT:
  class RBLeaf:
    def __init__(self,parent):
      self.size = 0
      self.parent = parent
    def isblack(self): return True
    def isred(self): return False
    def isleaf(self): return True
    def __str__(self): return "RBLeaf"
    def __len__(self): return 0
    def treestr(self,showpa=False):
      if showpa:
        pa = str(self.parent.value) if self.parent is not None else "-1"
        return ".["+pa+"]"
      else: return "."

  class RBNode:
    def __init__(self,value,black=True):
      self.value = value
      self.black = black
      self.size = 1
      self.l = pyRBT.RBLeaf(self)
      self.r = pyRBT.RBLeaf(self)
      self.parent = None
    def isblack(self): return self.black
    def isred(self): return not self.black
    def isleaf(self): return False
    def __len__(self): return self.size
    def __str__(self):
      return "RBNode("+str(self.value)+","+("black" if self.black else "red")+")"
    def treestr(self,showpa=False):
      if showpa:
        pa = "[" + (str(self.parent.value) if self.parent is not None else "-1") + "]"
      else: pa = ""
      col = "B" if self.black else "R"
      return "("+self.l.treestr()+","+str(self.value)+":"+col+pa+","+self.r.treestr()+")"
    def path(self):
      node = self
      while node is not None:
        yield node
        node = node.parent

  class RBIterator:
    def __init__(self,tree,reverse=False,retnodes=False):
      self.tree = tree
      self.node = None
      self.fwd = not reverse
      self.retnodes = retnodes
    def __iter__(self): return self
    def next(self): return self.__next__()
    def __next__(self):
      node = self.node
      if node is None:
        if self.tree.root.isleaf(): raise StopIteration() # empty tree
        node = self.tree.root
        if self.fwd:
          while not node.l.isleaf(): node = node.l
        else:
          while not node.r.isleaf(): node = node.r
      elif self.fwd and not node.r.isleaf():
        # Take the secondary fork (right fork when forward)
        node = node.r
        while not node.l.isleaf(): node = node.l
      elif not self.fwd and not node.l.isleaf():
        # Take the secondary fork (left fork when reverse)
        node = node.l
        while not node.r.isleaf(): node = node.r
      else:
        # Back up the tree - find first parent node that used left node
        if self.fwd:
          while node.parent is not None and node is node.parent.r: node = node.parent
        else:
          while node.parent is not None and node is node.parent.l: node = node.parent
        if node.parent is None: raise StopIteration()
        node = node.parent
      self.node = node
      return node if self.retnodes else node.value

  leaf = RBLeaf(None)

  def __init__(self):
    self.root = pyRBT.leaf

  def __len__(self):
    return self.root.size

  # Editing the tree voids any iterators! Do not edit the tree whilst iterating.
  def __iter__(self):
    return pyRBT.RBIterator(self,False,False)

  # Get a reverse iterator by overriding reversed(...)
  def __reversed__(self):
    return pyRBT.RBIterator(self,True,False)

  # Iterator that returns each node in order
  def nodes(self,reverse=False):
    return pyRBT.RBIterator(self,reverse,True)

  # Get a string representation of the tree
  def __str__(self):
    return self.root.treestr()

  # override the square bracket operator [] to get a value by index
  def __getitem__(self,i):
    return self.get(i)

  # setitem not defined since we don't map from key -> value
  # def __setitem__(self,key,value):

  # override the del operation to delete a value by index
  def __delitem__(self,i):
    self.pop(i)

  def __contains__(self,item):
    return self.find(item) is not None

  def clear(self):
    self.root = pyRBT.leaf

  # compare two Red Black Trees lexicographically
  # [1] < [2] < [1,1] < [1,2] < [1,2,0]
  def __cmp__(x,y):
    if len(x) != len(y): return len(x) - len(y)
    for (a,b) in zip(x,y):
      if a != b: return a-b
    return 0

  def __gt__(x,y): return x.__cmp__(y)  > 0
  def __ge__(x,y): return x.__cmp__(y) >= 0
  def __eq__(x,y): return x.__cmp__(y) == 0
  def __ne__(x,y): return x.__cmp__(y) != 0
  def __le__(x,y): return x.__cmp__(y) <= 0
  def __lt__(x,y): return x.__cmp__(y)  < 0

  @staticmethod
  def _grandparent(node):
    return node.parent.parent if node.parent is not None else None

  @staticmethod
  def _uncle(node):
    pa = node.parent
    if pa is None: return None
    gp = pa.parent
    if gp is None: return None
    return gp.r if pa == gp.l else gp.l

  @staticmethod
  def _sibling(node):
    pa = node.parent
    if pa is None: return None
    return pa.r if pa.l == node else pa.l

  # Replace child `ch` with `newch` in parent node `pa`
  def _replace_node(self,pa,ch,newch):
    if pa is None: self.root = newch
    elif pa.l is ch: pa.l = newch
    else: pa.r = newch
    newch.parent = pa

  #
  #   pa    ->    ch
  #  /  \        /  \
  # 1   ch      pa   3
  #    /  \    /  \
  #   2    3  1    2
  # pass pa node, returns ch node (new parent)
  def _rotate_left(self,node):
    pa, ch = node, node.r
    pa.r, ch.l = ch.l, pa
    ch.parent, pa.parent, pa.r.parent = pa.parent, ch, pa
    pa.size = len(pa.l) + 1 + len(pa.r)
    ch.size = len(ch.l) + 1 + len(ch.r)
    self._replace_node(ch.parent, pa, ch)
    return ch

  #
  #       pa    ->   ch
  #      /  \       /  \
  #     ch   3     1   pa
  #    /  \           /  \
  #   1    2         2    3
  # pass pa node, returns ch node (new parent)
  def _rotate_right(self,node):
    pa,ch = node,node.l
    pa.l, ch.r = ch.r, pa
    ch.parent, pa.parent, pa.l.parent = pa.parent, ch, pa
    pa.size = len(pa.l) + 1 + len(pa.r)
    ch.size = len(ch.l) + 1 + len(ch.r)
    self._replace_node(ch.parent, pa, ch)
    return ch

  def _insert_case1(self,node):
    # print("  tree:",self,"  insert_case1:",node)
    if node.parent is None:
      self.root = node
      self.root.black = True
    elif node.parent.isred():
      self._insert_case3(node)

  def _insert_case3(self,node):
    # print("  tree:",self,"  insert_case3:",node)
    assert node.parent is not None and node.parent.isred()
    # Assumption: parent exists and is red
    #  => therefore grandparent also exists and is black
    gp = pyRBT._grandparent(node)
    un = pyRBT._uncle(node)
    if un is not None and un.isred():
      node.parent.black = True
      un.black = True
      gp.black = False
      self._insert_case1(gp) # gp is now red, deal with it
    else:
      self._insert_case4(node)

  def _insert_case4(self,node):
    # print("  tree:",self,"  insert_case4:",node)
    gp = pyRBT._grandparent(node)
    pa = node.parent
    if node == pa.r and pa == gp.l:
      self._rotate_left(pa)
      node = pa
    elif node == pa.l and pa == gp.r:
      self._rotate_right(pa)
      node = pa
    self._insert_case5(node)

  def _insert_case5(self,node):
    # print("  tree:",self,"  insert_case5:",node)
    gp = pyRBT._grandparent(node)
    pa = node.parent
    gp.black = False
    pa.black = True
    if node == pa.l: self._rotate_right(gp)
    else: self._rotate_left(gp)

  # multiset = True allows multiple insertions of the same value
  def insert(self,item,multiset=False):
    if len(self) == 0: self.root = pyRBT.RBNode(item)
    else:
      # Add new node as a leaf node, then balance tree
      node = self.root
      while True:
        if not multiset and item == node.value:
          node.value = item
          return
        nxt = (node.l if item < node.value else node.r)
        if nxt.isleaf(): break
        node = nxt
      newv = pyRBT.RBNode(item,black=False)
      newv.parent = node
      if item < node.value: node.l = newv
      else: node.r = newv
      # Need to node update sizes
      while node is not None:
        node.size += 1
        node = node.parent
      # Re-balance tree
      self._insert_case1(newv)

  def extend(self,l,multiset=False):
    for x in l: self.insert(x,multiset)

  # remove element from a given index
  def pop(self,i=None):
    if i is None: i = len(self)-1
    node = self.getnode(i)
    return self._delete_node(node)

  # remove a given item
  def remove(self,item):
    node = self.findnode(item)
    if node is None: raise KeyError("RBT key '"+str(item)+"' not found")
    return self._delete_node(node)

  def _delete_node(self,dnode):
    node = dnode
    val = node.value # value that is being deleted
    # go right since we use the < and >= relations for left/right leaves
    if not node.r.isleaf():
      node = node.r
      while not node.l.isleaf(): node = node.l
    elif not node.l.isleaf():
      node = node.l
      while not node.r.isleaf(): node = node.r
    dnode.value = node.value # swap value into node to be deleted
    for v in node.path(): v.size -= 1
    self._delete_one_child(node)
    return val

  def _delete_one_child(self,node):
    child = (node.l if node.r.isleaf() else node.r)
    self._replace_node(node.parent, node, child)
    # may be appending a leaf node, this is OK in deletion
    if node.isblack():
      if child.isred(): child.black = True
      else: self._delete_case2(child)
    # `node` is no longer in the tree

  # assume we have a parent
  def _delete_case2(self,node):
    if node.parent is None: return
    (pa,nd,sb) = (node.parent,node,pyRBT._sibling(node))
    if sb.isred():
      pa.black = False
      sb.black = True
      if nd == pa.l: self._rotate_left(pa)
      else: self._rotate_right(pa)
    self._delete_case3(node)

  def _delete_case3(self,node):
    (pa,nd,sb) = (node.parent,node,pyRBT._sibling(node))
    if pa.isblack() and sb.isblack() and sb.l.isblack() and sb.r.isblack():
      sb.black = False
      self._delete_case2(pa) # parent
    else:
      self._delete_case4(node) # node

  def _delete_case4(self,node):
    (pa,nd,sb) = (node.parent,node,pyRBT._sibling(node))
    if pa.isred() and sb.isblack() and sb.l.isblack() and sb.r.isblack():
      sb.black = False
      pa.black = True
    else:
      self._delete_case5(node)

  def _delete_case5(self,node):
    (pa,nd,sb) = (node.parent,node,pyRBT._sibling(node))
    if sb.isblack():
      if nd == pa.l and sb.r.isblack() and sb.l.isred():
        sb.black = False
        sb.l.black = True
        self._rotate_right(sb)
      elif nd == pa.r and sb.l.isblack() and sb.r.isred():
        sb.black = False
        sb.r.black = True
        self._rotate_left(sb)
    self._delete_case6(node)

  def _delete_case6(self,node):
    (pa,nd,sb) = (node.parent,node,pyRBT._sibling(node))
    sb.black = pa.black
    pa.black = True
    if nd == pa.l:
      sb.r.black = True
      self._rotate_left(pa)
    else:
      assert nd == pa.r
      sb.l.black = True
      self._rotate_right(pa)

  def find(self,item):
    node = self.findnode(item)
    return node.value if node is not None else None

  def findnode(self,item,node=None):
    if node is None: node = self.root
    while not node.isleaf():
      if item == node.value: return node
      node = (node.l if item < node.value else node.r)
    return None

  # fetch via index
  # index is within `start` if passed
  def get(self,i,start=None):
    node = self.getnode(i,start)
    return node.value

  def getnode(self,i,start=None):
    node = self.root if start is None else start
    if i < 0: i += len(node) # allow negative indices
    if i < 0 or i >= len(node):
      raise IndexError("index out of range (%d vs 0..%d)" % (i, len(v)))
    while not node.isleaf():
      if i < len(node.l): node = node.l
      elif i == len(node.l): return node
      else:
        i -= len(node.l) + 1
        node = node.r
    raise RuntimeError("Internal pyRBT error")

  # Get the first index of an given value
  def index(self,item,start=None):
    node = self.root if start is None else start
    i = 0
    idx = None
    while not node.isleaf():
      if item < node.value: node = node.l
      elif item == node.value:
        # found one instance, look for earlier ones
        idx = i+len(node.l)
        node = node.l
      else:
        i += len(node.l) + 1
        node = node.r
    if idx is None: raise KeyError('Key not found: '+str(item))
    return idx

  # Check data structure integrity by checking invariants are met
  def check(self):
    assert (len(self) == 0) == self.root.isleaf() # size is zero only if empty
    assert self.root.isblack() # root node is black
    nblack = -1
    nnodes = 0
    for node in self.nodes():
      # print("Check:",'->'.join([str(x) for x in p]))
      assert not node.isleaf() or node.isblack() # all leaf nodes are black
      if node.isred():
        # all red nodes have only black children
        assert node.l.isblack() and node.r.isblack()
      # Every path from the the root has the same number of black nodes
      if node.l.isleaf() or node.r.isleaf():
        ntmpb = sum([ x.isblack() for x in node.path() ]) + 1
        assert nblack == -1 or nblack == ntmpb
        nblack = ntmpb
      nnodes += 1
    assert(nnodes == len(self))
    # print('nblack:',nblack,'nnodes:',nnodes)


import random

def _test_rbt_auto(nums):
  tree = pyRBT()
  vals = [] # sorted values in the tree
  # insert values into the tree
  for v in nums:
    tree.insert(v,True)
    vals.append(v)
    vals.sort()
    tree.check()
    assert sum([ x==y for x,y in zip(vals,iter(tree)) ]) == len(vals)
    # Test indexing
    for (i,v) in enumerate(vals): assert(tree[i] == v)
    for (i,v) in enumerate(vals): assert tree.index(v) == vals.index(v)
  # remove the values in a random order
  rvals = list(nums)
  random.shuffle(rvals)
  for v in rvals:
    tree.remove(v)
    vals.remove(v)
    tree.check()
    assert sum([ x==y for x,y in zip(vals,iter(tree)) ]) == len(vals)
    # Test indexing
    for (i,v) in enumerate(vals): assert tree[i] == v
    for (i,v) in enumerate(vals): assert tree.index(v) == vals.index(v)
  # Re-build sorted remove forwards
  sortedvals = sorted(vals)
  tree.extend(sortedvals)
  for v in sortedvals: assert sortedvals.remove(v) == tree.remove(v)
  assert len(tree) == 0
  tree.check()
  # Re-build sorted remove backwards
  sortedvals = sorted(vals)
  tree.extend(sortedvals)
  for v in reversed(sortedvals): assert sortedvals.remove(v) == tree.remove(v)
  assert len(tree) == 0
  tree.check()

def _test_rbt_autotests():
  print("Doing mixed automated tests...")
  vals = list(range(1,100))
  _test_rbt_auto(vals) # 1..N in sorted order
  # vals.reverse()
  # _test_rbt_auto(vals) # 1..N in reverse sorted order
  random.shuffle(vals)
  _test_rbt_auto(vals) # 1..N in random order
  _test_rbt_auto([]) # test epmty set
  _test_rbt_auto([random.randrange(100) for x in range(200)]) # rand with repeats
  _test_rbt_auto([random.randrange(1000) for x in range(200)]) # rand with repeats
  _test_rbt_auto([1]*10) # multiple 1s

def _test_rbt_comparison():
  print("Testing RBT comparison...")
  abc = pyRBT()
  xyz = pyRBT()
  abc.extend([1,2,3,9])
  xyz.extend([9,3,2,1])
  assert abc == xyz and abc >= xyz and abc <= xyz
  assert not (abc > xyz) and not (abc < xyz) and not (abc != xyz)
  abc.remove(3)
  # abc < xyz
  assert abc < xyz and xyz > abc and abc != xyz
  assert not (abc > xyz) and not (abc >= xyz) and not (abc == xyz)
  assert not (xyz < abc) and not (xyz <= abc)
  abc.clear()
  xyz.clear()
  # abc == xyz
  assert abc == xyz and abc <= xyz and abc >= xyz
  assert not (abc != xyz) and not (abc < xyz) and not (abc > xyz)
  # abc > xyz
  abc.insert(1)
  assert abc > xyz and xyz < abc and abc != xyz
  assert not (abc < xyz) and not (abc <= xyz) and not (abc == xyz)
  assert not (xyz > abc) and not (xyz >= abc)

def _test_rbt_index():
  print("Test index returns first index...")
  tree = pyRBT()
  tree.extend([3,2,1,1,2,3],multiset=True) # 1,1,2,2,3,3
  assert(len(tree) == 6)
  for i in range(1,4): assert(tree.index(i) == (i-1)*2)

def _test_red_black_tree():
  print("Testing RBT")

  # Insert [1,2,...,N]
  _test_rbt_autotests()

  # Test python features
  tree = pyRBT()
  vals = list(range(1,10))
  sortedvals = sorted(list(vals)) # sorted copy
  random.shuffle(vals)
  for v in vals:
    tree.insert(v,True)
    tree.check()
  # -- Testing iterate paths --
  # print("Testing path iteration...")
  # for path in tree.paths():
  #   print(' ','->'.join([str(x) for x in path]))
  # print("Testing path iterating reversed...")
  # for path in tree.paths(reverse=True):
  #   print(' ','->'.join([str(x) for x in path]))
  print("Testing value iteration...")
  assert ','.join([str(x) for x in tree]) == ','.join([str(x) for x in sortedvals])
  print("Testing value iteration reversed...")
  assert ','.join([str(x) for x in reversed(tree)]) == ','.join([str(x) for x in reversed(sortedvals)])
  print("Testing tree[i]...")
  for i in range(len(tree)): assert tree[i] == sortedvals[i]
  print("Testing find...")
  for f in [-1,0.5,len(vals)+1,len(vals)-3.6]: assert tree.find(f) is None
  print("Testing tree.index(i)...")
  for (i,v) in enumerate(sortedvals): assert tree.index(v) == sortedvals.index(v)
  print("Checking tree...")
  tree.check()
  # Test removing random nodes with pop
  while len(sortedvals) > 0:
    i = random.randrange(len(sortedvals))
    assert tree.pop(i) == sortedvals.pop(i)
    tree.check()
  # re-build tree and sorted list
  tree.extend(vals)
  sortedvals = sorted(list(vals)) # sorted copy
  assert sum([ x == y for (x,y) in zip(iter(tree),sortedvals)]) == len(vals)
  print("Testing remove...")
  for v in vals:
    tree.remove(v)
    tree.check()
  _test_rbt_comparison()
  _test_rbt_index()
  print("Looks like the tests all passed...")

if __name__ == '__main__':
  _test_red_black_tree()

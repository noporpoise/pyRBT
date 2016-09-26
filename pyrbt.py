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
    def __init__(self,tree,reverse=False,retnodes=False,nxt=None):
      # if node==None goto nxt, if node==None and nxt==None -> end of iteration
      self.tree = tree
      self.node = None
      self.fwd = not reverse
      self.retnodes = retnodes
      # set nxt to first node we want to visit
      if nxt is None and not tree.root.isleaf():
        nxt = tree.root
        if not reverse:
          while not nxt.l.isleaf(): nxt = nxt.l
        else:
          while not nxt.r.isleaf(): nxt = nxt.r
      self.nxt = nxt
    def __iter__(self): return self
    @staticmethod
    def next_node(node,tree,fwd,nxt=None):
      if node is None: return nxt
      elif fwd and not node.r.isleaf():
        # Take the secondary fork (right fork when forward)
        node = node.r
        while not node.l.isleaf(): node = node.l
      elif not fwd and not node.l.isleaf():
        # Take the secondary fork (left fork when reverse)
        node = node.l
        while not node.r.isleaf(): node = node.r
      else:
        # Back up the tree - find first parent node that used left node
        if fwd:
          while node.parent is not None and node is node.parent.r: node = node.parent
        else:
          while node.parent is not None and node is node.parent.l: node = node.parent
        node = node.parent
      return node
    def next(self): return self.__next__()
    def __next__(self):
      self.node = pyRBT.RBIterator.next_node(self.node,self.tree,self.fwd,self.nxt)
      if self.node is None: raise StopIteration()
      return self.node if self.retnodes else self.node.value
    def delete(self):
      self.nxt = pyRBT.RBIterator.next_node(self.node,self.tree,self.fwd,self.nxt)
      self.tree._delete_node(self.node)
      self.node = None

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
  def __getitem__(self,key):
    if isinstance(key, slice):
      return [ self[i] for i in range(*key.indices(len(self))) ]
    if isinstance(key, int):
      return self.get(key)
    raise TypeError("Invalid argument type.")

  # setitem not defined since we don't map from key -> value
  # def __setitem__(self,key,value):

  # override the del operation to delete a value by index
  def __delitem__(self,i):
    self.pop(i)

  def __contains__(self,item):
    return self.find(item) is not None

  def clear(self):
    self.root = pyRBT.leaf

  def __hash__(self):
    if len(self) == 0: return 0
    # djb2 by Dan Bernstein (http://stackoverflow.com/a/7666577/431087)
    h = 5381 # this is a prime
    for v in self: h = ((h*33) ^ hash(v)) & 0xffffffffffffffff
    return h

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

  # Swap two RBNodes
  def _swap_nodes(self,a,b):
    a.black,b.black = b.black,a.black
    a.value,b.value = b.value,a.value
    a.size,b.size = b.size,a.size
    apa,bpa = a.parent,b.parent
    self._replace_node(apa,a,b)
    self._replace_node(bpa,b,a)
    a.l,b.l = b.l,a.l
    a.r,b.r = b.r,a.r
    a.l.parent = a.r.parent = a
    b.l.parent = b.r.parent = b

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
    # Find bottom internal node to swap with
    node = dnode
    val = dnode.value
    # go right since we use the < and >= relations for left/right leaves
    if not node.r.isleaf():
      node = node.r
      while not node.l.isleaf(): node = node.l
    elif not node.l.isleaf():
      node = node.l
      while not node.r.isleaf(): node = node.r
    # swap value into node to be deleted
    if node is not dnode:
      self._swap_nodes(dnode,node)
      dnode.value,node.value = node.value,dnode.value
    for v in dnode.path(): v.size -= 1
    self._delete_one_child(dnode)
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
      raise IndexError("index out of range (%d vs 0..%d)" % (i, len(node)))
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
    assert nnodes == len(self)
    # print('nblack:',nblack,'nnodes:',nnodes)

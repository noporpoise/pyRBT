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

class pyRBT(object):
  __slots__ = ('root')

  class RBLeaf(object):
    __slots__ = ('size','parent')
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

  class RBNode(object):
    __slots__ = ('value','black','size','l','r','parent')
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
      """ Returns a generator that iterates up the tree starting with `node` """
      node = self
      while node is not None:
        yield node
        # assert node.parent is not node
        node = node.parent

  class RBTIterator(object):
    """
    Iterator over nodes in order. Supports forwards and backwards iteration,
    insertion into and deletion from the tree. Returns nodes, not their values.
    """
    __slots__ = ('tree','fwd','node','nxt')
    def __init__(self,tree,reverse=False,nxt=None):
      # if node==None goto nxt, if node==None and nxt==None -> end of iteration
      self.tree = tree
      self.fwd = not reverse
      self.node = None
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
      self.node = pyRBT.RBTIterator.next_node(self.node,self.tree,self.fwd,self.nxt)
      if self.node is None: raise StopIteration()
      self.nxt = None
      return self.node
    def prev(self): return self.__prev__()
    def __prev__(self):
      n = self.node if self.node is not None else self.nxt
      p = pyRBT.RBTIterator.next_node(n,self.tree,not self.fwd,None)
      if self.node is None: raise StopIteration()
      self.node = None
      self.nxt = n
      return p
    def delete(self):
      self.nxt = pyRBT.RBTIterator.next_node(self.node,self.tree,self.fwd,self.nxt)
      self.tree._delete_node(self.node)
      self.node = None
    def insert(self,v):
      return self.tree.insert(v)

  class RBTValIterator(RBTIterator):
    def __next__(self): return super(pyRBT.RBTValIterator,self).__next__().value
    def __prev__(self): return super(pyRBT.RBTValIterator,self).__prev__().value

  def __init__(self,lst=None):
    self.root = pyRBT.RBLeaf(None)
    if lst is not None: self.extend(lst)

  def __len__(self):
    return self.root.size

  # Editing the tree voids any iterators! Do not edit the tree whilst iterating.
  def __iter__(self):
    return pyRBT.RBTValIterator(self,False)

  # Get a reverse iterator by overriding reversed(...)
  def __reversed__(self):
    return pyRBT.RBTValIterator(self,True)

  def nodes(self,reverse=False):
    """ Iterator that returns each node in order """
    return pyRBT.RBTIterator(self,reverse)

  # Get a string representation of the tree
  def __str__(self):
    return self.root.treestr()

  # override the square bracket operator [] to get a value by index
  def __getitem__(self,key):
    if isinstance(key, slice):
      return [ self.get(i) for i in range(*key.indices(len(self))) ]
    elif isinstance(key, int):
      return self.get(key)
    else:
      raise TypeError("Invalid argument type.")

  # setitem not defined since we don't map from key -> value
  # def __setitem__(self,key,value):

  # override the del operation to delete a value by index
  def __delitem__(self,key):
    if isinstance(key, slice):
      # work backwards deleting items
      for i in reversed(range(*key.indices(len(self)))): self.pop(i)
    elif isinstance(key, int):
      self.pop(key)
    else:
      raise TypeError("Invalid argument type.")

  def __contains__(self,item):
    return self.find(item) is not None

  def clear(self):
    """ Reset the tree to an empty tree. """
    self.root = pyRBT.RBLeaf(None)

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
      if a != b: return -1 if a < b else 1
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

  def _replace_child_node(self,pa,ch,newch):
    """
    Replace child `ch` with `newch` in parent node `pa` and
    update parent of `newch`
    """
    if pa is None: self.root = newch
    elif pa.l is ch: pa.l = newch
    elif pa.r is ch: pa.r = newch
    else: raise Exception("No such child")
    newch.parent = pa

  def _swap_nodes(self, a, b):
    """ Swap the positions of two nodes in the tree """
    a.l,a.r,b.l,b.r, = b.l,b.r,a.l,a.r
    a.parent,b.parent = b.parent,a.parent
    # Keep size and black/red state with positions in tree
    a.size,b.size = b.size,a.size
    a.black,b.black = b.black,a.black
    # Remove self loops if nodes connected
    if a.parent is a: a.parent = b
    if b.parent is b: b.parent = a
    # register nodes with new parents (also resolves self-loops in children)
    self._replace_child_node(b.parent,a,b)
    self._replace_child_node(a.parent,b,a)
    # # register nodes with new children
    a.l.parent = a.r.parent = a
    b.l.parent = b.r.parent = b

  def _rotate_left(self,node):
    """
    Rotate node.right child into parent position, and parent into old left pos.
      pa    ->    ch
      /  \        /  \
     1   ch      pa   3
        /  \    /  \
       2    3  1    2
    pass pa node, returns ch node (new parent)
    """
    pa, ch = node, node.r
    pa.r, ch.l = ch.l, pa
    ch.parent, pa.parent, pa.r.parent = pa.parent, ch, pa
    pa.size = len(pa.l) + 1 + len(pa.r)
    ch.size = len(ch.l) + 1 + len(ch.r)
    self._replace_child_node(ch.parent, pa, ch)
    return ch

  def _rotate_right(self,node):
    """
    Rotate node.left child into parent position, and parent into old right pos.
         pa    ->   ch
        /  \       /  \
       ch   3     1   pa
      /  \           /  \
     1    2         2    3
    pass pa node, returns ch node (new parent)
    """
    pa,ch = node,node.l
    pa.l, ch.r = ch.r, pa
    ch.parent, pa.parent, pa.l.parent = pa.parent, ch, pa
    pa.size = len(pa.l) + 1 + len(pa.r)
    ch.size = len(ch.l) + 1 + len(ch.r)
    self._replace_child_node(ch.parent, pa, ch)
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

  def insert(self,item,multiset=False):
    """
    Add an item into the tree.
    :multiset True allows multiple insertions of the same value
    """
    if len(self) == 0: newv = self.root = pyRBT.RBNode(item)
    else:
      # Add new node as a leaf node, then balance tree
      node = self.root
      while True:
        if not multiset and item == node.value:
          node.value = item
          return node.value
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
    return newv.value

  def extend(self,l,multiset=False):
    """ Insert all the items form list l. """
    for x in l: self.insert(x,multiset)

  def pop(self,i=None):
    """ Remove and return an element at a given index. """
    if i is None: i = len(self)-1
    node = self.getnode(i)
    return self._delete_node(node)

  def remove(self,item):
    """ remove a given item from the tree """
    node = self.findnode(item)
    if node is None: raise KeyError("RBT key '"+str(item)+"' not found")
    return self._delete_node(node)

  @staticmethod
  def _adjacent_node(node):
    """ Fetch an adjacent node on either the left or right of a node. """
    if not node.l.isleaf():
      # adjacent node to the left
      node = node.l
      while not node.r.isleaf(): node = node.r
    elif not node.r.isleaf():
      # adjacent node to the right
      node = node.r
      while not node.l.isleaf(): node = node.l
    return node

  def _delete_node(self,node):
    # Find bottom internal node to swap with
    adjnode = pyRBT._adjacent_node(node)
    # swap node to the bottom of the tree
    if adjnode is not node: self._swap_nodes(adjnode,node)
    for v in node.path(): v.size -= 1
    self._delete_node_with_one_child(node)
    return node.value

  def _delete_node_with_one_child(self,node):
    """ Delete node with at most one child. """
    child = (node.l if node.r.isleaf() else node.r)
    self._replace_child_node(node.parent, node, child)
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
    (pa,sb) = (node.parent,pyRBT._sibling(node))
    if pa.isblack() and sb.isblack() and sb.l.isblack() and sb.r.isblack():
      sb.black = False
      self._delete_case2(pa)
    else:
      self._delete_case4(node)

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
    """ Find a given item in the tree. Returns None if not found. """
    node = self.findnode(item)
    return node.value if node is not None else None

  def findnode(self,item,node=None):
    """ Find the node holding a given value. Returns None if not found. """
    if node is None: node = self.root
    while not node.isleaf():
      if item == node.value: return node
      node = (node.l if item < node.value else node.r)
    return None

  def get(self,i,start=None):
    """ Fetch item via index. Index is within `start` if passed """
    node = self.getnode(i,start)
    return node.value

  def getnode(self,i,start=None):
    """ Find the node holding the i-th item. """
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

  def index(self,item,start=None):
    """ Get the first index of an given value """
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

  def union(self,other):
    """ Return a tree that is the union of this tree and other """
    tree = pyRBT()
    tree.extend(self)
    tree.extend(other)
    return tree

  def diff(self,other):
    """ Return a tree contain elements from this tree not in other tree """
    tree = pyRBT()
    for x in self:
      if x not in other:
        tree.insert(x)
    return tree

  def intersect(self,other):
    """ Return a tree that is the intersection of this tree and other """
    tree = pyRBT()
    ai,bi = iter(self),iter(other)
    try:
      a,b = next(ai),next(bi)
      while True:
        if a==b:
          tree.insert(a)
          a,b = next(ai),next(bi)
        elif a < b: a = next(ai)
        else: b = next(bi)
    except StopIteration: pass
    return tree

  def symmetric_diff(self,other):
    """ Return a tree that contains elements that are only in one of self,other. """
    tree = pyRBT()
    ai,bi = iter(self),iter(other)
    try:
      a,b = next(ai),next(bi)
      while True:
        if a==b: a,b = next(ai),next(bi)
        elif a < b: tree.insert(a); a = next(ai)
        else: tree.insert(b); b = next(bi)
    except StopIteration: pass
    tree.extend(ai)
    tree.extend(bi)
    return tree

  def check(self):
    """ Check data structure integrity by checking invariants are met. """
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

class pyRBMap(pyRBT):
  class RBKeyValue(object):
    """ RBKeyValue compares only the key but also store a value """
    def __init__(self,k,v=None): self.k,self.v = k,v
    def __cmp__(x,y): return -1 if (x.k<y.k) else 1
    def __gt__(x,y): return a.k >  b.k
    def __ge__(x,y): return x.k >= y.k
    def __eq__(x,y): return x.k == y.k
    def __ne__(x,y): return x.k != y.k
    def __le__(x,y): return x.k <= y.k
    def __lt__(x,y): return x.k <  y.k

  class RBMapIterator(pyRBT.RBTIterator):
    def __next__(self):
      x = super(pyRBMap.RBMapIterator,self).__next__().value
      return (x.k, x.v)
    def __prev__(self):
      x = super(pyRBMap.RBMapIterator,self).__prev__().value
      return (x.k, x.v)
    def insert(self,k,v):
      return super(pyRBMap.RBMapIterator,self).insert(RBKeyValue(k,v))

  def __init__(self,h=None):
    super(pyRBMap,self).__init__()
    if h is not None: self.extend(h)

  def __cmp__(x,y):
    """ order by (key, value) for each element """
    if len(x) != len(y): return len(x) - len(y)
    for ((ak,av),(bk,bv)) in zip(x,y):
      if ak != bk: return -1 if ak < bk else 1
      if av != bv: return -1 if av < bv else 1
    return 0

  def insert(self,k,v):
    return super(pyRBMap,self).insert(pyRBMap.RBKeyValue(k,v)).v

  def extend(self,h):
    for k,v in h.items():
      self.insert(k,v)

  def remove(self,item):
    return super(pyRBMap,self).remove(pyRBMap.RBKeyValue(item)).v

  def __setitem__(self,k,v):
    self.insert(k,v)

  def __getitem__(self,key):
    if isinstance(key, slice):
      return [ self.find(pyRBMap.RBKeyValue(x)).v for x in range(*key.indices(len(self))) ]
    if isinstance(key, int):
      return self.find(pyRBMap.RBKeyValue(key)).v
    raise TypeError("Invalid argument type.")

  def __contains__(self,item):
    return self.find(pyRBMap.RBKeyValue(item)) is not None

  def __delitem__(self,k):
    """
    del(h[x]) in pyRBMap is different to del(t[i]) in pyRBT, as in pyRBT we
    delete the i-th element, here we delete element with (key) value x.
    """
    self.remove(k)

  def keys(self,reverse=False):
    """ Generator for keys (ordered by key) """
    for k,v in self:
      yield k

  def values(self,reverse=False):
    """ Generator for values (ordered by key) """
    for k,v in self:
      yield v

  def keyvalues(self,reversed=False):
    """ Generator for (key,value) pairs """
    return pyRBMap.RBMapIterator(self,reversed)

  def __iter__(self): return pyRBMap.RBMapIterator(self)
  def __reversed__(self): return pyRBMap.RBMapIterator(self,True)

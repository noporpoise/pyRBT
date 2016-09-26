from __future__ import print_function
from pyrbt import pyRBT
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
    assert v == tree.remove(v)
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

def _test_splice():
  print("Testing splice")
  tree = pyRBT()
  assert tree[:] == [] # empty splice
  l = [1,2,3,4]
  tree.extend(l)
  for i in range(len(l)):
    for j in range(i,len(l)):
      if tree[i:j] != l[i:j]:
        print("MISMATCH",i,j,tree[i:j],l[i:j])
      assert tree[i:j] == l[i:j]

def _test_hash():
  print("Testing hash()...")
  a = pyRBT()
  b = pyRBT()
  a.extend([3, 10, 2, 7, 1, 4, 6, 5, 8, 9])
  b.extend([4, 8, 9, 3, 6, 1, 2, 10, 5, 7])
  assert hash(a) == hash(b) and a == b
  # Randomised hash test
  a.clear()
  b.clear()
  l = [ random.randrange(100) for i in range(100) ]
  random.shuffle(l)
  a.extend(l)
  random.shuffle(l)
  b.extend(l)
  assert hash(a) == hash(b) and a == b

def _test_delete():
  print("Testing delete...")
  t = pyRBT()
  t.extend([4, 8, 9, 3, 6]) # 3,4,6,8,9
  t.remove(4)
  assert list(t) == [3,6,8,9]

def _test_itr_delete():
  print("Testing iterator delete...")
  t = pyRBT()
  # test removing all whilst iterating
  t.extend([4, 8, 9, 3, 6])
  i = iter(t)
  for x in i: i.delete()
  assert len(t) == 0
  # test removing even numbers
  t.extend([4, 8, 9, 3, 6]) # 3,4,6,8,9
  i = iter(t)
  for x in i:
    if x % 2 == 0: i.delete()
  assert len(t) == 2

def main():
  print("Testing RBT")
  _test_splice()
  _test_hash()
  _test_delete()
  _test_itr_delete()

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
  main()
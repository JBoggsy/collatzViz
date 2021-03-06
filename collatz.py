from PIL import Image
from random import randint
import subprocess, sys

class collatzGen(object):
    """
    Simple generator for a collatz sequence starting at integer n.
    """
    def __init__(self, n):
        if n < 1:
            raise ValueError("Initial number must be greater than 0")
        self.nextVal = n
        self.num = n
        self.series = []

    def __iter__(self):
        return self

    def next(self):
        """
        Returns the next number of the collatz sequence, or raises StopIteration
        if the last number returned was 1.
        """
        self.nextVal = self.num
        if self.num == 0:
            raise StopIteration()
        if self.num % 2 == 0:
            self.num = self.num / 2
            self.series.append(self.num)
            return self.nextVal
        else:
            if self.num == 1:
                self.num = 0
                return self.nextVal
            else:
                self.num = 3 * self.num + 1
                self.series.append(self.num)
                return self.nextVal


class collatzTree(object):
    """
    Tree-like object to hold the tree of connections produced by combined collatz
    series. Each node has either 1 or 2 children. The traditional tree structure,
    although a good graphical/mental representation of combined collatz sequences,
    falls very short for my purposes, because finding the location of a particular
    number reuires running the collatz series for it all over again, since we
    currently don't know how to traverse the tree towards a goal. We save
    computational resources at the expense of storage resources by actually storing
    the tree as a dictionary, where each node is a key and its 1 or 2 children are
    the values. Because nodes in this tree will always be ints > 0, no special
    objects are used. This means tree traversal works by looking up the root node
    in the dict, using the associated values as children, and navigate to them by
    looking them up in the dict. All ctzTrees start with the root node 1 and its
    immediate child 2. Leaves of the tree will always have an empty list as their
    value.

    WARNING: UNLIKE TRADITIONAL TREES, WE CANNOT ASSUME THE GRAPH IS CONNECTED!
    AN INTERRUPTION IN ADDING A SEQUENCE MAY RESULT IN "FLOATING" NODES /BRANCHES!
    """
    def __init__(self):
        self.tree = {1: [2]}

    def __add_child(self, parent, child):
        """
        Adds a child to a node, first checking its validity and that it isn't a
        repeat.
        """
        if child != (2 * parent) and child != ((parent - 1) / 3):
            raise ValueError("child should precede parent in a collatz sequence")
        if child in self.tree[parent]:
            raise AttributeError("child is already a child of parent node")
        self.tree[parent].append(child)
        if child not in self.tree:
            self.tree[child] = []

    def __add_parent_and_child(self, parent, child):
        """
        Adds both a parent node and its child, "floating" in the tree. This
        COMPLETELY BREAKS traditional assumptions about trees!
        """
        if parent in self.tree:
            self.__add_child(self, parent, child)
            return
        if child != (2 * parent) and child != ((parent - 1) / 3):
            raise ValueError("child should precede parent in a collatz sequence")
        self.tree[parent] = [child]
        self.child = []

    def add_sequence(self, n):
        """
        Adds the collatz sequence from `n` to 1 to the tree, stopping when it first
        encounters a number already in the tree.
        """
        ctzGen = collatzGen(n)
        child = ctzGen.next()
        if child not in self.tree:
            self.tree[child] = []
        for parent in ctzGen:
            if parent in self.tree:
                # print(str(parent) + " in tree!")
                try:
                    # print("    trying to add child " + str(child))
                    self.__add_child(parent, child)
                except AttributeError as e:
                    # print("    child " + str(child) + " already in tree")
                    return
                return
            # print(str(parent) + " not in tree, adding it and " + str(child))
            self.__add_parent_and_child(parent, child)
            child = parent

    def build_tree(self, n):
        """
        Builds the tree by adding sequences from 1 to n.
        """
        for x in xrange(1, n):
            self.add_sequence(x)

    def generate_dot_file(self):
        """
        Generates a .gv file for displaying the collatz tree.
        """
        dot_text = "digraph cltzTree {"
        queue = [1]
        while queue != []:
            parent = queue.pop(0)
            childs = self.tree[parent]
            for child in childs:
                queue.append(child)
                dot_text += "\n\t{c} -> {p};".format(p=parent, c=child)
        dot_text += "\n}"
        return dot_text

    def display_tree(self):
        """
        Uses the generate_dot_file() command to create a graphviz gv file and
        then displays it.
        """
        dotFileText = self.generate_dot_file()
        with open("collatzTreeFile.gv", "w") as writeFile:
            writeFile.write(dotFileText)
        subprocess.call(["dot", "collatzTreeFile.gv", "-Tpng", "-ocollatzTreeViz.png"])
        subprocess.call(["eog", "collatzTreeViz.png"])


    def __str__(self):
        return str(self.tree)


if __name__ == '__main__':
    ctzTree = collatzTree()
    ctzTree.build_tree(int(sys.argv[1]))
    print(ctzTree.display_tree())
    print(len(ctzTree.tree))

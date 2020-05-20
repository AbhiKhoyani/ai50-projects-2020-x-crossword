import sys

from crossword import *
import random
import math


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for domain in self.domains[var].copy():
                if var.length != len(domain):
                    self.domains[var].remove(domain)
                
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        result = False
        if (x,y) in list(self.crossword.overlaps.keys()):
            i,j = self.crossword.overlaps[(x,y)]
            for domain_x in self.domains[x].copy():
                remove = True
                for domain_y in self.domains[y]-{domain_x}:
                    if domain_x[i] == domain_y[j]:
                        remove = False
                        break
                    remove = remove and True
                if remove:
                    self.domains[x].remove(domain_x)
                    result= True
        return result


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs==None:
            arcs = set()
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.add((x,y))
        #print(arcs)
        while len(arcs)!=0:
            (x,y) = random.sample(arcs,1)[0]
            arcs.remove((x,y))
            if self.revise(x,y):
                if len(self.domains[x])==0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.add((z,x))
        return True 
                

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment)==len(self.crossword.variables):
            return True
        else:
            return False    

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #variables = list(self.crossword.variables)
        #neighbors = self.overlaps
        
        #1.            
        for assign in assignment:
            if len(assignment[assign]) != assign.length:
                #print(f"len is {len(assignment[var])},{var.length}")
                return False
            #3.     
            for neighbor in self.crossword.neighbors(assign):
                if neighbor not in assignment:
                    break
                i,j = self.crossword.overlaps[(assign,neighbor)]
                #print("temp",i,j,assign,neighbor)
                #print(setElement(assignment[assign]))
                #print(setElement(assignment[neighbor]))
                if assignment[assign][i]!=assignment[neighbor][j]:
                    #print("3",assign,neighbor)
                    return False
        #2.
        for value in list(assignment.values()):
            if list(assignment.values()).count(value)>1:
                #print("2",value, list(assignment.values()).count(value))
                return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #print(var)
        orders = {k:0 for k in self.domains[var]}
        neighbor = list(self.crossword.neighbors(var))
        #print(f"neighbor is {neighbor}")
        for order in orders: #order is domain 
            for n in neighbor:  # n is variable
                #print(n)
                #if len(assignment[n])== 1:
                #    break
                assignment[var]=order
                for n_domain in self.domains[n].copy():
                    a1 = assignment.copy() 
                    a1[n]=n_domain
                    #print(assignment)
                    if not self.consistent(a1):
                        #self.domains[n].remove(n_domain)
                        orders[order]+=1
        orders = sorted(orders.items(),key = lambda kv:kv[1])
        orders = list(i[0] for i in orders)
        return orders              

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        options = self.crossword.variables.difference(set(assignment.keys()))
        #print(options)
        min_val = math.inf
        neigh_num = -math.inf
        candidate = None
        for option in options:
            if len(self.domains[option])<min_val:
                min_val = len(self.domains[option])
                candidate = option
                neigh_num = len(self.crossword.neighbors(option))
            elif len(self.domains[option])==min_val:
                if len(self.crossword.neighbors(option)) >= neigh_num:
                    candidate = option
                    neigh_num = len(self.crossword.neighbors(option))
        return candidate

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            #print(value)
            a1 = assignment.copy()
            a1[var]=value
            #print(a1)
            if self.consistent(a1): 
                assignment[var]=value
                #print(assignment)
                arcs = {(neighbor,var) for neighbor in self.crossword.neighbors(var)}
                #print(arcs)
                if self.ac3(arcs):
                    for n in self.crossword.neighbors(var):
                        if len(self.domains[n])==1:
                            assignment[n]=setElement(self.domains[n])
                            #print('ac3 finished')
                result=self.backtrack(assignment)
                if result:
                    return result
                assignment.pop(var)
                for n in self.crossword.neighbors(var):
                    if n in assignment:
                        assignment.pop(n)
        return False

    #def Inference(self,assignment):
        
def setElement(set):
    for e in set:
        break
    return e

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

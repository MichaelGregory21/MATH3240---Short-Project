from enum import Enum
from queue import Queue

'''
Object type for infinity and negative infinity values
Useful for graph traversal algorithms
'''
class values(Enum):
        _neg_inf = 1
        _inf = 2

        '''
        Overload greater than relation
        Infinity defined to be greater than negative infinity and every float/int
        '''
        def __gt__(self, other):
            if self.__class__ is other.__class__:
                return self.value > other.value
            if isinstance(other,(int,float)):
                return self is self._inf

        '''
        Overload less than relation
        Negative infinity defined to be less than infinity and every float/int
        '''
        def __lt__(self, other):
            if self.__class__ is other.__class__:
                return self.value < other.value
            if isinstance(other,(int,float)):
                return self is self._neg_inf

        '''
        Overload repr value
        Used when printing values as elements of lists
        '''
        def __repr__(self):
            return '∞' if self.value == 2 else '-∞'

        '''
        Overload string value
        '''
        def __str__(self):
            return '∞' if self.value == 2 else '-∞'

        '''
        We define infinity + x = infinity + infinity = infinity for every float/int x
                  negative infinity + x = negative infinity + negative infinity = negative infinity
        '''
        def __add__(self, other):
            if isinstance(other,(float,int)):
                return self
            if self.__class__ is other.__class__:
                if self.value == other.value:
                    return self
            NotImplemented

        '''
        Addition is commutative
        '''
        def __radd__(self, other):
            return self + other

'''
A graph is a pair of sets; of vertices and of edges
Edges are edge-type. Vertices may be any object
A graph may be directed
'''
class Graph:
    
    '''
    An edge is a pair of vertices together with a weight and a label
    A weight is a float which is 0.0 by default
    A label is a string which is None by default
    '''
    class _Edge:        
        def __init__(self, u, v, weight:float=0.0, label:str=None):
            self._u = u
            self._v = v
            self._label = label
            self._weight = weight

        '''
        Returns true if this edge is incident to the given vertex. False, otherwise
        '''
        def isIncident(self, v) -> bool:
            return self._u is v or self._v is v

        '''
        Returns the edge pointing in the opposite direction.
        This edge has the same weight and label
        '''
        def reverse(self):
            return Graph._Edge(self._v, self._u, self._label, self._weight)

        '''
        Returns 'u' if the given index is 0, 'v' if the given index is 1, None, otherwise
        '''
        def __getitem__(self, index:int):
            if index == 0:
                return self._u
            elif index == 1:
                return self._v

        '''
        Overload string value
        '''
        def __str__(self):
            if self._label is not None: return "(" + str(self._label) + "," + str(self._weight) + ")"
            if self._weight == 0.0: return "(" + str(self._u) + "," + str(self._v) + ")"
            else: return str(self._weight) + "(" + str(self._u) + "," + str(self._v) + ")"

        '''
        Overload repr value
        Used when printing values as elements of lists
        '''
        def __repr__(self):
            return str((self._u, self._v)) if self._weight == 0.0 else str((self._u, self._v, self._weight))

        '''
        Overload equal relation
        Two edges are equal if they have the same endpoints
        '''
        def __eq__(self, other):
            return other._u == self._u and other._v == self._v

        '''
        Overload the hash relation
        returns the hash of the tuple (u,v)
        '''
        def __hash__(self):
            return hash((self._u, self._v))

        '''
        NotImplemented
        '''
        def __add__(self, other):
            if self.__class__ is other.__class__:
                NotImplemented
            else: return self
                
    def __init__(self, vertices:set={}, edges:set={}, directed:bool=False):
        self._vertices = vertices
        self._directed = directed
        self._edges = set()
        self._populate_edges(edges)

    '''
    Private method used in constructor to populate the edge set
    '''
    def _populate_edges(self, edges:set):
        for edge in edges:
            if not edge[0] in self._vertices or not edge[1] in self._vertices:
                raise ValueError("Edges must be between vertices contained in the graph")
            else:
                if isinstance(edge, tuple):
                    if len(edge) == 2:
                        self._edges.add(self._Edge(edge[0], edge[1]))
                        if not self._directed: self._edges.add(self._Edge(edge[1], edge[0]))
                    elif len(edge) == 3:
                        self._edges.add(self._Edge(edge[0], edge[1], edge[2]))
                        if not self._directed: self._edges.add(self._Edge(edge[1], edge[0], edge[2]))
                    elif len(edge) == 4:
                        self._edges.add(self._Edge(edge[0], edge[1], edge[2], edge[3]))
                        if not self._directed: self._edges.add(self._Edge(edge[1], edge[0], edge[2], edge[3]))
                elif isinstance(edge, self._Edge):
                    self._edges.add(edge)
                    if not self._directed: self._edges.add(edge.reverse())

    '''
    Add edge to this graph with the given endpoints, label, and weight
    '''
    def new_edge(self, u, v, label:str=None, weight:float=0.0):
        if not u in self._vertices and v in self._vertices:
            raise ValueError(str(u) + " and  " + str(v) + " are not valid vertices")
        self._edges.add(self._Edge(u,v, label, weight))
        if not self._directed: self._edges.add(self._Edge(v,u, label, weight))

    '''
    Uses dijkstra's algorithm to find the length of the shortest path between the given vertex and every other vertex
    Returns result as a dictionary
    '''
    def dijkstra(self, vertex) -> dict:
        vertices = list(self._vertices)
        vertices.sort()
        if not vertex in vertices:
            raise ValueError(str(vertex) + " not in graph")
        visited = set()
        distances = {vertex:values._inf for vertex in vertices}
        distances[vertex] = 0
        q = Queue()
        q.put(vertex,0)
        while not q.empty():
            current = q.get()
            if not current in visited:
                visited.add(current)
                for neighbor in self.neighbors(current):
                    tentative_dist = distances[current] + self._edge_weight(current, neighbor)
                    if distances[neighbor] > tentative_dist:
                        distances[neighbor] = tentative_dist

                        q.put(neighbor,distances[neighbor])
        return distances        

    '''
    Uses floyd-warshall's algorithm to return a matrix whose (i,j)-entry is the length of the shortest path between vertex i and j sorted in the natural fashion (i.e., alphabetical, numerical, etc.)
    '''
    def floyd_warshall(self,show_steps=False):
        vertices = list(self._vertices)
        vertices.sort()
        D = Matrix([[0 for v in vertices] for v in vertices])
        for i in range(len(vertices)):
            D[i][i] = 0
            for j in [j for j in range(len(vertices)) if j != i]:
                if self._are_neighbors(vertices[i],vertices[j]):
                    D[i][j] = self._edge_weight(vertices[i],vertices[j])
                else:
                    D[i][j] = values._inf
        for k in range(len(vertices)):
            if show_steps:
                print(D)
                print()
            for i in range(len(vertices)):
                for j in range(len(vertices)):
                    D[i][j] = min(D[i][j], D[i][k] + D[k][j])
        return D

    '''
    Uses dijkstra's algorithm to find the length of the longest, shortest path between every vertex
    '''
    def eccentricity(self, vertex=None):
        if vertex == None: return ({self.eccentricity(v) for v in self._vertices})
        return max(self.dijkstra(vertex).values())

    '''
    Returns the neighbors of the given vertex
    '''
    def neighbors(self, vertex):
        return {v for v in self._vertices if self._are_neighbors(vertex,v)}

    '''
    Returns true if the given vertices are neighbors. False, otherwise
    '''
    def _are_neighbors(self, v1, v2) -> bool:
        return self._Edge(v1,v2) in self._edges

    '''
    Returns the edge with the given endpoints if there is one. None, otherwise
    '''
    def _get_edge(self, v1, v2):
        if not self._Edge(v1,v2) in self._edges: return None
        for edge in self._edges:
            if edge._u == v1 and edge._v == v2: break
        return edge

    '''
    Returns the weight of the edge with the given endpoints if there is one. Infinity, otherwise
    '''
    def _edge_weight(self,v1,v2):
        if not self._are_neighbors(v1,v2): return values._inf
        else: return self._get_edge(v1, v2)._weight

    '''
    Returns true if this graph is connected. False, otherwise
    '''
    def is_connected(self):
        return all([isinstance(i,(int,float)) for i in self.floyd_warshall()])

    '''
    Returns the adjacency matrix of this graph
    '''
    def adjacency(self):
        vertices = list(self._vertices)
        vertices.sort()
        return Matrix([[1 if self._are_neighbors(i,j) else 0 for i in vertices] for j in vertices])

    '''
    Returns the adjacency list of this graph
    '''
    def adjacency_list(self):
        vertices = list(self._vertices)
        vertices.sort()
        return "\n".join([str(str(v) + ": " + ", ".join([str(u) for u in vertices if self._are_neighbors(u,v)])) for v in vertices])

    '''
    Overload the sum operator
    If the summand is a graph, returns the graph with union of the vertices and union of edges
    If the summand is not a graph, adds it to this graph as an element of the vertex set
    '''
    def __add__(self, other):
        if isinstance(other, Graph): # If other is a graph, combine vertices and edges
            return Graph(self._vertices.union(other._vertices), self._edges.union(other._edges), self._directed or other._directed)
        return Graph(self._vertices.add(other), self._edges) # If other is not a graph, add it as a vertex

    def __sub__(self, other):
        if isinstance(other, self._Edge): # If other is an edge, remove it from the list of edges
            return Graph(self._vertices, self._edges - other)
        if isinstance(other, Graph): # If other is a graph, remove ever vertex in other from self and all edges adjacent to these
            if not other._vertices.issubset(self._vertices):
                raise ValueError("other graph is not a subgraph")
            for vertex in other._vertices:
                self._vertices = self._vertices.difference({vertex})
                self._edges = self._edges.difference({e for e in self._edges if e.isIncident(vertex)})
            return self
        return self - Graph({other}) # If other is neither an edge, nor a graph, try to remove the singleton graph containing only other as a vertex

    '''
    Overload the str value
    '''
    def __str__(self):
        if self._directed:
            return "{" + ", ".join([str(v) for v in self._vertices]) + "}" + ", " + "{" + ", ".join([str(e) for e in self._edges]) + "}"
        reduced = set()
        for edge in self._edges:
            if not edge.reverse() in reduced: reduced.add(edge)
        return "{" + ", ".join([str(v) for v in self._vertices]) + "}" + ", " + "{" + ", ".join([str(e) for e in reduced]) + "}"

'''
A matrix is a grid of elements given as a list of lists.
Each row must be the same length but this may be arbitrary and there may be arbitrarily many of them
'''
class Matrix:
        def __init__(self, matrix):
            if not all([len(row) == len(matrix[0]) for row in matrix]):
                raise ValueError("All rows must be the same length")
            self._matrix = matrix
            
        '''
        Returns the (i,j) component of this matrix
        '''
        def __getitem__(self, index):
            return self._matrix[index]

        '''
        Overload the sum operator
        The summand must be a matrix with compatible dimension
        '''
        def __add__(self, other):
            if not isinstance(other, Matrix):
                raise TypeError("Expected matrix type")
            if self.width() != other.width or self.height() != other.height():
                raise ValueError("Incompatible matrices")
            return Matrix([[self[i][j] + other[i][j] for j in range(self.width())] for i in range(self.height())])

        '''
        Overload the difference operator
        The subtrahend must be a matrix with compatible dimension
        Returns this + (-1) * other
        '''
        def __sub__(self, other):
            return self + (-1 * other)

        '''
        Overload the product operator
        If the multiplier is a float/int, returns this matrix multiplied component-wise
        If the multiplier is a matrix, returns the product using matrix multiplication
        '''
        def __mul__(self, other):
            if isinstance(other, (int,float)):
                return Matrix([[other * self[i][j] for j in range(self.width())] for i in range(self.height())])
            if isinstance(other, Matrix):
                if other.height() != self.width():
                    raise ValueError("Incompatible matrices")
                return Matrix([[sum(self[i][k] * other[k][j] for k in range(other.height())) for j in range(other.width())] for i in range(self.height())])
            raise TypeError("Expected matrix type")

        '''
        Right multiplication must not be matrix type since it has later instantiation
        Thus, type must be int/float and is performed component-wise
        '''
        def __rmul__(self, other):
            return self * other

        '''
        Overload power operator
        Returns the n-th product of this matrix with itself
        The exponent must be integer type
        '''
        def __pow__(self, other):
            if isinstance(other, int) and self.height() == self.width():
                if other >= 1:
                    result = self
                    index = 1
                    while index < other:
                        result *= self
                        index += 1
                    return result
                elif other == 0:
                    return Matrix([[1 if i == j else 0 for i in range(self.height())] for j in range(self.height())])
            raise ValueError("Expected square matrix for base and integer exponent")
                
        '''
        Overload the string value
        '''
        def __str__(self):
            max_width = max(len(str(element)) for row in self._matrix for element in row)
            Matrix_str = "\n".join("[" + " ".join(f"{str(element):>{max_width}}" for element in row) + "]" for row in self._matrix)
            return Matrix_str

        '''
        Yields matrix elements from left to right, top to bottom
        '''
        def __iter__(self):
            for row in self._matrix:
                for j in row:
                    yield j

        '''
        Returns the height of this matrix
        '''
        def height(self) -> int:
            return len(self._matrix)

        '''
        Returns the width of this matrix
        '''
        def width(self) -> int:
            return len(self._matrix[0])

        '''
        Returns the determinant of this matrix using minors and cofactors
        '''
        def det(self):
            if not self.height() == self.width():
                raise ValueError("Expected square Matrix")
            if self.height() == 2:
                return self[0][0] * self[1][1] + (-1) * self[0][1] * self[1][0]
            else:
                return sum([(-1)**i * self[0][i] * self.minor(i,0).det() for i in range(self.width())])

        '''
        Returns the p,q minor of this matrix
        '''
        def minor(self, p, q):
            if not 0 <= p <= self.width() - 1 or not 0 <= q <= self.height() - 1:
                raise ValueError("index out of bounds")
            return Matrix([[self[j][i] for i in range(self.width()) if i!=p] for j in range(self.height()) if j!=q])

        '''
        Returns the matrix of cofactors of this matrix
        '''
        def cofactor(self):
            if self.height() == 2 and self.width() == 2:
                return Matrix([[self[1][1], (-1) * self[1][0]], [(-1) * self[0][1], self[0][0]]])
            return Matrix([[self._cofactor(i,j) for i in range(self.width())] for j in range(self.height())])

        '''
        Returns the p,q cofactor of this matrix
        '''
        def _cofactor(self, p, q):
            return (-1)**(p+q) * self.minor(p,q).det()
                


edges =      {(1,3),(1,4),(1,8),(1,9),
              (2,3),(2,6),(2,7),
              (3,1),(3,2),(3,7),(3,8),
              (4,1),(4,10),(4,16),
              (5,6),(5,12),(5,13),
              (6,2),(6,5),(6,13),(6,19),(6,20),
              (7,2),(7,3),(7,8),(7,14),
              (8,1),(8,3),(8,7),(8,9),(8,14),(8,15),
              (9,1),(9,8),(9,15),
              (10,4),(10,16),(10,17),(10,18),
              (11,12),(11,18),(11,24),(11,25),
              (12,5),(12,11),(12,13),(12,19),(12,25),
              (13,5),(13,6),(13,12),(13,19),
              (14,7),(14,8),(14,15),(14,21),
              (15,8),(15,9),(15,14),(15,21),
              (16,4),(16,10),(16,17),(16,22),
              (17,10),(17,16),(17,18),(17,22),(17,23),
              (18,10),(18,11),(18,17),(18,23),(18,24),(18,29),
              (19,6),(19,12),(19,13),(19,20),(19,25),
              (20,6),(20,19),
              (21,14),(21,15),(21,26),
              (22,16),(22,17),(22,23),(22,27),
              (23,17),(23,18),(23,22),(23,27),(23,28),(23,29),
              (24,11),(24,18),(24,25),(24,29),(24,30),
              (25,11),(25,12),(25,19),(25,24),(25,30),(25,31),
              (26,21),(26,32),(26,33),
              (27,22),(27,23),(27,28),(27,33),(27,34),(27,35),
              (28,23),(28,27),(28,29),(28,35),
              (29,18),(29,23),(29,24),(29,28),(29,30),(29,35),
              (30,24),(30,25),(30,29),(30,31),
              (31,25),(31,30),(31,36),
              (32,26),(32,33),(32,38),
              (33,26),(33,27),(33,32),(33,38),
              (34,27),(34,35),(34,39),
              (35,27),(35,28),(35,29),(35,34),(35,39),(35,40),
              (36,31),(36,37),(36,41),
              (37,36),(37,41),(37,42),
              (38,32),(38,33),
              (39,34),(39,35),(39,40),
              (40,35),(40,39),
              (41,36),(41,37),(41,42),
              (42,37),(42,41)}



RISK = Graph({1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42},
             {(e[0],e[1],1)for e in edges})



print(RISK.adjacency())
print()
print("---------------------------------------------------------------------------------------------")
print()
print(RISK.adjacency_list())

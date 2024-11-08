import numpy as np
from collections import deque
import copy

class MaximumFlowAlgo:
    def __init__(self, graph):
        """Graph object

        Args:
            graph (_type_): adjacent matrix of graph
        """
        self.graph = copy.deepcopy(graph )
        self.n_vertex = len(graph)


class Edmond_Karps(MaximumFlowAlgo):
    def __init__(self, graph):
        super().__init__(graph)

    def _bfs(self, source: int, sink: int, parent: list):
        visited = [False]*(self.n_vertex) 
        queue = deque([source]) # init queue, add source
        visited[source] = True
        while queue:
            u = queue.popleft()
            for ind, val in enumerate(self.graph[u]):
                # for each connected vertex and edge capacity
                if visited[ind] == False and val > 0:
                    # if vertex is not visted and capacity >0 
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u # save current vertex (u) as parent of connected vertex (ind)
                    if ind == sink:
                        return True 
        return False # no path from source -> sink
    
    def execute(self, source: int, sink: int):
        parent = [-1]*(self.n_vertex) # init parent of every vertex as -1 
        max_flow = 0 
        # Augment the flow while there is path from source to sink
        while self._bfs(source, sink, parent):
            path_flow = float("Inf")
            s = sink 
            while (s != source):
                path_flow = min(path_flow, self.graph[parent[s]][s]) # min path bottleneck
                s= parent[s]

            max_flow += path_flow 
            v = sink
            while(v != source):
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]

        return max_flow

class Edge:
    def __init__(self, v: int, flow:int, C:int, rev:int):
        """Object represent and edge

        Args:
            v (int): The destination vertex index
            flow (int): Current flow through edge
            C (int): Capacity of edge
            rev (int): Index of reverve edge
        """
        self.v = v        
        self.flow = flow  
        self.C = C       
        self.rev = rev 

class Dinic(MaximumFlowAlgo):
    def __init__(self, graph):
        super().__init__(graph)
        self.adj = [[] for i in range(self.n_vertex)]
        self.level = [0 for i in range(self.n_vertex)]
        self.adjacent_matrix_to_edge()


    def add_edge(self, u:int, v:int, C:int):
        """Add forward edge from u->v and backward edge from v->u
        Forward edge u-> v: flow = 0, capacity = capacity
        Backward edge v-> u: flow =0, capacity = 0
        Args:
            u (int): start vertex index
            v (int): destination vertex index
            C (int): edge capacity
        """
        a = Edge(v, 0, C, len(self.adj[v]))
        b = Edge(u, 0, 0, len(self.adj[u]))
        self.adj[u].append(a)
        self.adj[v].append(b) 

    def adjacent_matrix_to_edge(self):
        """Create edge object based on adjacent matrix"""
        for u_id, u_row in enumerate(self.graph):
            for v_id, edge in enumerate(u_row):
                if edge >0:
                    self.add_edge(u = u_id, v = v_id, C = edge)
        
    def _bfs(self, source:int, sink:int):
        """BFS search + construct level graph 

        Args:
            source (int): source vertex
            sink (int): destination vertext

        Returns:
            Bool: True if exits path from source to sink. False otherwise 
        """
        # init every vertex level as -1 
        for i in range(self.n_vertex):
            self.level[i] = -1
        # Level of source vertex
        self.level[source] = 0

        queue = deque([source])
        while queue:
            u = queue.popleft()
            for i in range(len(self.adj[u])):
                e = self.adj[u][i] # loop through each edge connecting to vertex u 
                if self.level[e.v] < 0 and e.flow < e.C:
                    self.level[e.v] = self.level[u]+1 # level of target vertex is level of current vertext + 1 
                    queue.append(e.v)

        return False if self.level[sink] < 0 else True

    def sendFlow(self, u: int, flow:int, sink:int, start: list):
        """_summary_

        Args:
            u (int): current vertext
            flow (int): current flow 
            t (int): sink
            start (list): array keeping track of which edges we've explored from each vertex
        Returns:
            _type_: _description_
        """

        # Sink reached
        if u == sink:
            return flow
 
        # Traverse all adjacent edges one -by -one
        while start[u] < len(self.adj[u]):
 
            # Pick next edge from adjacency list of u
            e = self.adj[u][start[u]]
            if self.level[e.v] == self.level[u]+1 and e.flow < e.C: # check if edge can be used: destination edge must = current level vertex + 1 and flow is not saturated 
 
                # find minimum flow from u to t
                curr_flow = min(flow, e.C - e.flow)
                temp_flow = self.sendFlow(e.v, curr_flow, sink, start)
 
                # flow is greater than zero
                if temp_flow and temp_flow > 0:
 
                    # add flow to current edge
                    e.flow += temp_flow
 
                    # subtract flow from reverse edge
                    # of current edge
                    self.adj[e.v][e.rev].flow -= temp_flow
                    return temp_flow
            start[u] += 1
        
    def execute(self, source, sink):
        if source == sink:
            return 0
        total = 0
        while self._bfs(source, sink) == True:
            start = [0 for i in range(self.n_vertex+1)]
            while True:
                flow = self.sendFlow(source, float('inf'), sink, start)
                if not flow:
                    break
                total += flow

        # return maximum flow
        return total



if __name__ == "__main__":
    # test case
    graph = [[0, 16, 13, 0, 0, 0],
        [0, 0, 10, 12, 0, 0],
        [0, 4, 0, 0, 14, 0],
        [0, 0, 9, 0, 0, 20],
        [0, 0, 0, 7, 0, 4],
        [0, 0, 0, 0, 0, 0]]
    
    source =0 
    sink = 5
    g = Edmond_Karps(graph)
    print("The maximum possible flow is %d " % g.execute(source, sink))

    g = Dinic(graph)
    print("The maximum possible flow is %d " % g.execute(source, sink))


    

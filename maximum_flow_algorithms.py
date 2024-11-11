# maximum_flow_algorithms.py

import numpy as np
from collections import deque
import copy
import json 

class MaximumFlowAlgo:
    def __init__(self, graph):
        """Graph object

        Args:
            graph (list of lists): Adjacency matrix of the graph
        """
        self.graph = copy.deepcopy(graph)
        self.n_vertex = len(graph)

class Edmond_Karps(MaximumFlowAlgo):
    def __init__(self, graph):
        super().__init__(graph)
        self.paths = []  # To store paths and their flows

    def _bfs(self, source: int, sink: int, parent: list):
        visited = [False] * self.n_vertex
        queue = deque([source])  # Initialize queue with source
        visited[source] = True
        while queue:
            u = queue.popleft()
            for ind, val in enumerate(self.graph[u]):
                # For each connected vertex and edge capacity
                if not visited[ind] and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u  # Save current vertex as parent of connected vertex
                    if ind == sink:
                        # Build the path from source to sink
                        path = []
                        v = sink
                        while v != source:
                            path.insert(0, v)
                            v = parent[v]
                        path.insert(0, source)
                        return True, path
        return False, []  # No path from source to sink

    def execute(self, source: int, sink: int):
        parent = [-1] * self.n_vertex  # Initialize parent of every vertex as -1
        max_flow = 0
        self.paths = []

        # Augment the flow while there is a path from source to sink
        while True:
            found_path, path = self._bfs(source, sink, parent)
            if not found_path:
                break
            # Find minimum residual capacity along the path
            path_flow = float("Inf")
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s])  # Min path bottleneck
                s = parent[s]

            # Add path and flow to paths list
            self.paths.append({'path': path, 'flow': path_flow})

            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]

        return max_flow

class Edge:
    def __init__(self, v: int, flow: int, C: int, rev: int):
        """Object representing an edge

        Args:
            v (int): The destination vertex index
            flow (int): Current flow through edge
            C (int): Capacity of edge
            rev (int): Index of reverse edge in destination's adjacency list
        """
        self.v = v
        self.flow = flow
        self.C = C
        self.rev = rev

class Dinic(MaximumFlowAlgo):
    def __init__(self, graph):
        super().__init__(graph)
        self.adj = [[] for _ in range(self.n_vertex)]
        self.level = [0 for _ in range(self.n_vertex)]
        self.paths = []  # To store blocking flows (paths and their flows)
        self.adjacent_matrix_to_edge()

    def add_edge(self, u: int, v: int, C: int):
        """Add forward edge from u->v and backward edge from v->u"""
        a = Edge(v, 0, C, len(self.adj[v]))
        b = Edge(u, 0, 0, len(self.adj[u]))
        self.adj[u].append(a)
        self.adj[v].append(b)

    def adjacent_matrix_to_edge(self):
        """Create edge objects based on the adjacency matrix"""
        for u_id, u_row in enumerate(self.graph):
            for v_id, edge in enumerate(u_row):
                if edge > 0:
                    self.add_edge(u=u_id, v=v_id, C=edge)

    def _bfs(self, source: int, sink: int):
        """BFS search to construct level graph"""
        # Initialize every vertex level as -1
        self.level = [-1] * self.n_vertex
        # Level of source vertex
        self.level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for e in self.adj[u]:
                if self.level[e.v] == -1 and e.flow < e.C:
                    self.level[e.v] = self.level[u] + 1
                    queue.append(e.v)
        return self.level[sink] != -1

    def sendFlow(self, u: int, flow: int, sink: int, start: list, path: list):
        """DFS to send flow after levels have been assigned"""
        if u == sink:
            self.paths.append({'path': path.copy(), 'flow': flow})
            return flow

        while start[u] < len(self.adj[u]):
            e = self.adj[u][start[u]]
            if self.level[e.v] == self.level[u] + 1 and e.flow < e.C:
                curr_flow = min(flow, e.C - e.flow)
                path.append(e.v)
                temp_flow = self.sendFlow(e.v, curr_flow, sink, start, path)
                if temp_flow > 0:
                    e.flow += temp_flow
                    self.adj[e.v][e.rev].flow -= temp_flow
                    return temp_flow
                path.pop()
            start[u] += 1
        return 0

    def execute(self, source: int, sink: int):
        if source == sink:
            return 0
        total = 0
        while self._bfs(source, sink):
            start = [0] * self.n_vertex
            while True:
                path = [source]
                flow = self.sendFlow(source, float('Inf'), sink, start, path)
                if flow == 0:
                    break
                total += flow
        return total

class FordFulkerson(MaximumFlowAlgo):
    def __init__(self, graph):
        super().__init__(graph)
        self.paths = []  # To store paths and their flows

    def _dfs(self, source: int, sink: int, visited: list, flow: float):
        """Depth-First Search to find an augmenting path"""
        if source == sink:
            return flow, [sink]
        visited[source] = True
        for v in range(self.n_vertex):
            if not visited[v] and self.graph[source][v] > 0:
                current_flow = min(flow, self.graph[source][v])
                result_flow, path = self._dfs(v, sink, visited, current_flow)
                if result_flow > 0:
                    self.graph[source][v] -= result_flow
                    self.graph[v][source] += result_flow
                    path.insert(0, source)
                    return result_flow, path
        return 0, []

    def execute(self, source: int, sink: int):
        max_flow = 0
        self.paths = []

        while True:
            visited = [False] * self.n_vertex
            flow, path = self._dfs(source, sink, visited, float('Inf'))
            if flow == 0:
                break
            max_flow += flow
            self.paths.append({'path': path, 'flow': flow})

        return max_flow

if __name__ == "__main__":
    # Test case
    graph = [
        [0, 16, 13, 0, 0, 0],
        [0, 0, 10, 12, 0, 0],
        [0, 4, 0, 0, 14, 0],
        [0, 0, 9, 0, 0, 20],
        [0, 0, 0, 7, 0, 4],
        [0, 0, 0, 0, 0, 0]
    ]
    
    source = 0 
    sink = 5

    # Edmond-Karps
    g = Edmond_Karps(graph)
    print("Edmond-Karps: The maximum possible flow is %d " % g.execute(source, sink))
    print("Edmond-Karps: Paths: " , g.paths)

    # Dinic
    g = Dinic(graph)
    print("Dinic: The maximum possible flow is %d " % g.execute(source, sink))
    print("Dinic: Paths: " , g.paths)
    # Ford-Fulkerson
    g = FordFulkerson(graph)
    print("Ford-Fulkerson: The maximum possible flow is %d " % g.execute(source, sink))
    print("Ford-Fulkerson: Paths: " , g.paths)

    print('TEST RUN ON MAP DATA')
    with open('./road_network_data.json', encoding='utf-8') as file:
        data = json.load(file)

    graph = data['adjacent_matrix']
    node_name_lookup = data['node_name_lookup']
    node_id_lookup = data['node_index_lookup']
    source_name = 'Hang Xanh Intersection'
    sink_name = 'Tan Son Nhat International Airport'
    source = node_id_lookup.get(str(node_name_lookup.get(source_name)))
    sink = node_id_lookup.get(str(node_name_lookup.get(sink_name)))
    print(source, sink)

    # Edmond-Karps
    g = Edmond_Karps(graph)
    print("Edmond-Karps: The maximum possible flow is %d " % g.execute(source, sink))
    print("Edmond-Karps: Paths: " , g.paths)

    # Dinic
    g = Dinic(graph)
    print("Dinic: The maximum possible flow is %d " % g.execute(source, sink))
    print("Dinic: Paths: " , g.paths)

    # Ford-Fulkerson
    g = FordFulkerson(graph)
    print("Ford-Fulkerson: The maximum possible flow is %d " % g.execute(source, sink))
    print("Ford-Fulkerson: Paths: " , g.paths)

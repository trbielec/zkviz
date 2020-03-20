import networkx as nx
import plotly.graph_objs as go


class NetworkPlotly:
    def __init__(self, name="Zettelkasten"):
        """
        Build network to visualize with Plotly

        Parameters
        ----------
        name : str
            The network name.
        """
        self.graph = nx.Graph()


    def add_node(self, node_id):
    # def add_node(self, node_id, title):
        """
        Add a node to the network.

        Parameters
        ----------
        node_id : str, or int
            A  unique identifier for the node, typically the zettel ID.
        title : str
            The text label for each node, typically the zettel title.

        """
        # self.graph.add_node(node_id, title=title)
        self.graph.add_node(node_id)

    def add_edge(self, source, target):
        """
        Add a node (a zettel) to the network.

        Parameters
        ----------
        source : str or int
            The ID of the source zettel.
        target : str or int
            The ID of the target (cited) zettel.

        """
        self.graph.add_edge(source, target)

    def build_plotly_figure(self, pos=None):
        """
        Creates a Plot.ly Figure that can be view online or offline.

        Parameters
        ----------
        graph : nx.Graph
            The network of zettels to visualize
        pos : dict
            Dictionay of zettel_id : (x, y) coordinates where to draw nodes. If
            None, the Kamada Kawai layout will be used.

        Returns
        -------
        fig : plotly Figure

        """

        # remove disconnected nodes
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))

        if pos is None:
            if len(self.graph) < 10000:
                pos = nx.layout.fruchterman_reingold_layout(self.graph, iterations=100)
                # pos = nx.layout.kamada_kawai_layout(self.graph)
            else:
                pos = nx.layout.random_layout(self.graph)

        # Create scatter plot of the position of all notes
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale="YlGnBu",
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15, title="Adjacency", xanchor="left", titleside="right"
                ),
                line=dict(width=0.3),
            ),
        )

        for node in self.graph.nodes():
            x, y = pos[node]
            text = "<br>".join([node, self.graph.nodes[node].get("node_id", "")])
            node_trace["x"] += tuple([x])
            node_trace["y"] += tuple([y])
            node_trace["text"] += tuple([text])

        # Color nodes based on the centrality
        # for node, centrality in nx.degree_centrality(self.graph).items():
        #     node_trace["marker"]["color"] += tuple([centrality])

        node_adjacencies = []
        node_text = []
        for node, adjacencies in enumerate(self.graph.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
        # node_trace.marker.size = node_adjacencies
        node_trace.marker.color = node_adjacencies



        # Draw the edges as annotations because it's only sane way to draw arrows.
        edges = []
        for from_node, to_node in self.graph.edges():
            edges.append(
                dict(
                    # Tail coordinates
                    ax=pos[from_node][0],
                    ay=pos[from_node][1],
                    axref="x",
                    ayref="y",
                    # Head coordinates
                    x=pos[to_node][0],
                    y=pos[to_node][1],
                    xref="x",
                    yref="y",
                    # Aesthetics
                    arrowwidth=1,
                    arrowcolor="#666",
                    arrowhead=2,
                    # Have the head stop short 5 px for the center point,
                    # i.e., depends on the node marker size.
                    standoff=5,
                )
            )

        fig = go.Figure(
            data=[node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=edges,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        return fig

    def render(self, output, view=False):
        """
        Render the network to disk.

        Parameters
        ----------
        output : str
            Name of the output file.
        view : bool
            Open the rendered network using the default browser. Default is
            False.

        """
        fig = self.build_plotly_figure()
        if not output.endswith(".html"):
            output += ".html"
        fig.write_html(output, auto_open=view)

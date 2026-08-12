import networkx as nx
import matplotlib.pyplot as plt


class NetworkIllustrator:
    def __init__(self, junctions, loads, soft_faults=None):
        self.junctions = junctions
        self.loads = loads
        self.soft_faults = soft_faults
        self.G = nx.DiGraph()

    def create_graph(self):
        # Add nodes and edges for junctions
        input_port_id = "J0"
        self.G.add_node(input_port_id, type="input")
        for junction in self.junctions:
            junc_id = junction[0]
            junc_id = "J" + junc_id
            branches_number = junction[3]
            self.G.add_node(junc_id, type="junction", branches_number=branches_number)
            parent_id = junction[1]
            parent_id = "J" + parent_id
            distance_to_parent = junction[2]
            if parent_id is not None:
                self.G.add_edge(parent_id, junc_id, distance=distance_to_parent)

        # Add nodes and edges for loads
        for load in self.loads:
            load_id = load[0]
            load_id = "L" + load_id
            impedance = load[3]
            self.G.add_node(load_id, type="load", impedance=impedance)
            parent_id = load[1]
            parent_id = "J" + parent_id
            distance_to_parent = load[2]
            if parent_id is not None:
                self.G.add_edge(parent_id, load_id, distance=distance_to_parent)

        # Add nodes and edges for soft faults
        if self.soft_faults:
            for soft_fault in self.soft_faults:
                fault_id = soft_fault[0]
                fault_id = "J" + fault_id
                impedance = soft_fault[3]
                self.G.add_node(fault_id, type="soft_fault", impedance=impedance)
                parent_id = soft_fault[1]
                parent_id = "J" + parent_id
                distance_to_parent = soft_fault[2]
                if parent_id is not None:
                    self.G.add_edge(parent_id, fault_id, distance=distance_to_parent)

    def draw_graph(self, filename, weighted=False):
        plt.clf()

        if weighted:
            pos = self.get_weighted_positions()
        else:
            pos = nx.nx_agraph.graphviz_layout(self.G, prog="dot")

        node_colors = [
            (
                "blue"
                if self.G.nodes[node]["type"] == "junction"
                else (
                    "green"
                    if self.G.nodes[node]["type"] == "load"
                    else (
                        "red" if self.G.nodes[node]["type"] == "soft_fault" else "green"
                    )
                )
            )
            for node in self.G.nodes()
        ]
        nx.draw(
            self.G,
            pos,
            with_labels=False,
            node_color=node_colors,
            node_size=700,
            font_size=10,
            font_color="white",
            arrows=True,
        )
        edge_labels = {
            edge: f"{float(data):.2f}"
            for edge, data in nx.get_edge_attributes(self.G, "distance").items()
        }

        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=14)

        # Add impedance labels to the load nodes
        load_labels = dict()
        for node in self.G.nodes():
            if self.G.nodes[node]["type"] == "load":
                impedance = float(self.G.nodes[node]["impedance"])
                if impedance > 1e4:
                    impedance_label = "Open Circuit"
                else:
                    impedance_label = f"Z={impedance:.2f}"
                load_labels[node] = impedance_label

        for node, label in load_labels.items():
            x, y = pos[node]
            plt.text(
                x,
                y,
                label,
                fontsize=12,
                ha="center",
                va="bottom",
                bbox=dict(facecolor="white", alpha=0.8),
            )

        plt.savefig(filename + ".png", format="png")
        # plt.show()

    def get_weighted_positions(self):
        # Calculate positions manually to make edge lengths proportional to distance
        pos = {}
        pos["J0"] = (0, 0)  # Start at the origin
        current_y = 0

        def calculate_positions(node, current_x, current_y):
            children = list(self.G.successors(node))
            if not children:
                return

            total_distance = sum(
                float(self.G[node][child]["distance"]) for child in children
            )
            next_x = current_x + total_distance

            for child in children:
                distance = float(self.G[node][child]["distance"])
                current_y += distance  # Increment y based on distance
                pos[child] = (next_x, current_y)
                calculate_positions(child, next_x, current_y)

        calculate_positions("J0", 0, 0)
        return pos


if __name__ == "__main__":
    junctions_input = [
        ("1", "0", 0.0, 3),
        ("3", "1", 5.0, 1),
    ]

    loads_input = [
        ("6", "3", 4.0, 1.5),
        ("7", "3", 4.0, 1.5),
        ("4", "2", 3.0, 0),
    ]

    soft_faults = [("2", "1", 1.0, 2)]

    ni = NetworkIllustrator(junctions_input, loads_input, soft_faults)
    ni.create_graph()
    ni.draw_graph("figure")

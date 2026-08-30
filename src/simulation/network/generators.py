import networkx as nx

def generate_watts_strogatz(n: int, k: int, p: float, seed: int = None) -> nx.Graph:
    """
    Generate a Watts-Strogatz small-world graph.
    Represents dense local household communities with some cross-community links.
    """
    return nx.watts_strogatz_graph(n=n, k=k, p=p, seed=seed)

def generate_barabasi_albert(n: int, m: int, seed: int = None) -> nx.Graph:
    """
    Generate a Barabási-Albert scale-free graph.
    Represents influencer-driven dynamics with highly connected hub nodes.
    """
    return nx.barabasi_albert_graph(n=n, m=m, seed=seed)

def generate_network(n: int, config, seed: int = None) -> nx.Graph:
    """Wrapper to generate network based on config."""
    if config.topology == "watts_strogatz":
        return generate_watts_strogatz(n=n, k=config.ws_k, p=config.ws_p, seed=seed)
    elif config.topology == "barabasi_albert":
        return generate_barabasi_albert(n=n, m=config.ba_m, seed=seed)
    else:
        raise ValueError(f"Unknown topology: {config.topology}")

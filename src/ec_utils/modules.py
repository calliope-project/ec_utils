"""Functions to aid in workflow modularisation."""

from pathlib import Path

import networkx as nx


def _modularise_snakemake_graph(
    rulegraph: nx.DiGraph, module_prefixes: list[str]
) -> nx.DiGraph:
    """Wrap module rules into a single rule with a special marker."""
    labels = nx.get_node_attributes(rulegraph, "label")
    # Ensure labels are clean strings
    labels = {key: value.replace('"', "") for key, value in labels.items()}

    modulegraph = rulegraph.copy()
    for prefix in module_prefixes:
        module_node_attrs = dict(label=prefix, color="0 0 0", style="diagonals")
        modulegraph.add_node(prefix, **module_node_attrs)

        module_nodes = set(
            key for key, value in labels.items() if value.startswith(prefix)
        )
        if not module_nodes:
            raise ValueError(f"Prefix not found: {prefix}.")
        for edge in rulegraph.edges:
            if not set(edge) - module_nodes:
                # edge is completely within the module
                modulegraph.remove_edge(*edge)
            elif edge[0] in module_nodes and edge[1] not in module_nodes:
                # edge is a module output
                modulegraph.add_edge(prefix, edge[1])
            elif edge[0] not in module_nodes and edge[1] in module_nodes:
                # edge is a module input
                modulegraph.add_edge(edge[0], prefix)

        modulegraph.remove_nodes_from(module_nodes)

    return modulegraph


def write_snakemake_modulegraph_png(
    snakemake_dotfile: Path | str, output_path: Path | str, prefixes: str|list[str]
):
    """Create a PNG file with a simplified DAG with a single rule per module.

    Args:
        snakemake_dotfile (Path | str): path to .dot file (e.g., a rulegraph).
        output_path (Path | str): location to save the resulting PNG.
        prefixes (str|list[str]): list of module prefixes to simplify.

    Raises:
        ValueError: input was not a .dot file.
    """
    if not str(snakemake_dotfile).endswith(".dot"):
        raise ValueError("Only .dot files can be processed.")
    if isinstance(prefixes, str):
        prefixes = [prefixes]

    rulegraph = nx.DiGraph(nx.nx_pydot.read_dot(snakemake_dotfile))

    modulegraph = _modularise_snakemake_graph(rulegraph, prefixes)
    dot_graph = nx.drawing.nx_pydot.to_pydot(modulegraph)
    dot_graph.write_png(output_path)

import ec_utils.modules as modules
import networkx as nx
import pytest


@pytest.fixture()
def rulegraph_path():
    return "tests/_example_files/rulegraph.dot"


@pytest.fixture()
def rulegraph(rulegraph_path):
    return nx.DiGraph(nx.nx_pydot.read_dot(rulegraph_path))


@pytest.fixture()
def modulegraph_path(tmp_path):
    return tmp_path / "modulegraph.png"


@pytest.mark.parametrize(
    "prefixes", [("module_biofuels"), ("module_hydropower", "module_wind_pv")]
)
def test_modulegraph_success(rulegraph_path, modulegraph_path, prefixes):
    """Correct configurations should run without issues."""
    modules.write_snakemake_modulegraph_png(rulegraph_path, modulegraph_path, prefixes)
    assert modulegraph_path.exists()


@pytest.mark.parametrize("prefix", [("module_fail"), ("module _ hydropower")])
def test_modulegraph_incorrect_prefix(rulegraph_path, modulegraph_path, prefix):
    """Users should be warned when requesting incorrect module names."""
    with pytest.raises(ValueError, match=f"Prefix not found: {prefix}."):
        modules.write_snakemake_modulegraph_png(
            rulegraph_path, modulegraph_path, prefix
        )


def test_modulegraph_incorrect_file_input(modulegraph_path):
    """Users should be warned if passing an incorrect file."""
    with pytest.raises(ValueError, match="Only .dot files can be processed."):
        modules.write_snakemake_modulegraph_png(
            "some_file.txt", modulegraph_path, "module_biofuels"
        )

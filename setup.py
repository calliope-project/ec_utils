#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="ec_utils",
    version="0.1.0",  # additionally defined in __init__.py
    description="Utilities for ec_modules.",
    maintainer="calliope-project",
    maintainer_email="ivan.ruizmanuel@tudelft.nl",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy", # TODO readd after solving #262
        "scipy", # TODO readd after solving #262
        "pandas", # TODO readd after solving #262
        "xarray", # TODO readd after solving #262
        "pycountry==18.12.8" # TODO readd after solving #262
    ],
    extras_require={
        "geo": [
            "geopandas", # TODO readd after solving #262
            "rasterio", # TODO readd after solving #262
            "rasterstats", # TODO readd after solving #262
        ],
    },
    entry_points={
        "mkdocs.plugins": [
            "dag = eurocalliopelib.docs.dag:DAGPlugin",
            "schema = eurocalliopelib.docs.schema:SchemaPlugin",
            "add-file = eurocalliopelib.docs.addfile:AddFilePlugin",
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
)

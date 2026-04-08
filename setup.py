# -*- coding: utf-8 -*-
import os
from setuptools import setup

current_path = os.path.abspath(os.path.dirname(__file__))

requirements = (
        "tracklib",
        "osgeo",
        "fiona",
        "shapely",
        ""
)

setup (
    name="OutdoorFootprintNetworkPipeline",
    version="1.0.0",
    description="OFNP is an open-source Python processing pipeline (MIT license) for generating outdoor activity footprint networks from GNSS trajectories, representing, for example, hikers’ or runners’ footprints within a defined spatial and temporal extent.",
    long_description="See ...",
    url="https://github.com/umrlastig/OutdoorFootprintNetworkPipeline",
    download_url= '',
    author="Marie-Dominique Van Damme, Yann Méneroux",
    author_email="todo@ign.fr",
    keywords=[],
    license="MIT License",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
    ],
    packages = ['ofnp','ofnp.algo','ofnp.pipeline','ofnp.util'],
    install_requires=requirements
)

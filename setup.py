# -*- coding: utf-8 -*-
"""Installer for the plone.app.multilingualindexes package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="plone.app.multilingualindexes",
    version="2.0",
    description="Multilingual Catalog Indexes for Plone",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Jens W. Klein",
    author_email="jk@kleinundpartner.at",
    url="https://pypi.python.org/pypi/plone.app.multilingualindexes",
    license="GPL version 2",
    packages=find_packages("src"),
    namespace_packages=["plone", "plone.app"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=["Products.CMFPlone", "setuptools"],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.multilingual[test]",
            "plone.app.querystring",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

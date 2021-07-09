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
    version="3.0.0.dev0",
    description="Multilingual Catalog Indexes for Plone",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python, Plone, multilingual, translation",
    author="Jens W. Klein",
    author_email="jk@kleinundpartner.at",
    url="https://github.com/plone/plone.app.multilingualindexes",
    license="GPL version 2",
    packages=find_packages("src"),
    namespace_packages=["plone", "plone.app"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.CMFPlone>=5.2.1",
        "plone.app.querystring>=1.4.14",
        "plone.app.theming>=4.1.3",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.multilingual[test]",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

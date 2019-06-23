try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="copinicoos",
    version="0.0.1",
    packages=["copinicoos"],
    description="Copernicus Downloader Bot",
    author="Sherry aka potatowagon",
    author_email="e0007652@u.nus.com",
    url="https://github.com/potatowagon/copinicoos",
    keywords=["copinicoos", "copernicus", "downloader", "radar", "ESA", "EU", "satellite"],
    install_requires=["colorama>=0.3.4"],
    extras_require={
        "dev": [
            "codecov>=2.0.15",
            "colorama>=0.3.4",
            "tox>=3.9.0",
            "tox-travis>=0.12",
            "pytest>=4.6.2",
            "pytest-cov>=2.7.1",
            "Sphinx>=1.7.4",
            "sphinx-autobuild>=0.7",
            "sphinx-rtd-theme>=0.3",
        ]
    },
    python_requires="==3.7",
)
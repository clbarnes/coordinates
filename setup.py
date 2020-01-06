import os
from setuptools import setup, find_packages
from runpy import run_path

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    readme = f.read()

vers_dict = run_path(os.path.join(here, "coordinates", "version.py"))

with open(os.path.join(here, "coordinates", "version.py")) as f:
    exec(f.read())


setup(
    name="coordinates",
    version=vers_dict["__version__"],
    packages=find_packages(exclude=("tests",)),
    url="https://github.com/clbarnes/coordinates",
    license="MIT",
    author="Chris L Barnes",
    author_email="barnesc@janelia.hhmi.org",
    description="Convenience class for doing maths with explicit coordinates",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="coordinate spatial mathdict",
    python_requires=">=3.6",
)

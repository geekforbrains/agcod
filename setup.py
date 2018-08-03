import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agcod",
    version="0.1.0",
    author="Gavin Vickery",
    author_email="gavin@geekforbrains.com",
    description="A tool for Amazon Gift Code On-Demand (AGCOD)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geekforbrains/agcod",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

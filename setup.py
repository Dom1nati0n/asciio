from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ascio",
    version="2.0.0",
    author="Dom1nati0n",
    description="CPU-Only ASCII Renderer & World Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "numpy",
    ],
    python_requires=">=3.6",
)
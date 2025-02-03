from setuptools import setup, find_packages

setup(
    name="veritas_fact_check_api",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
) 
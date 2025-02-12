from setuptools import setup, find_packages

setup(
    name="intelligent-api-gateway",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "fastapi",
        "uvicorn",
    ]
)

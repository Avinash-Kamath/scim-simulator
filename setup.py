from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scim-sim",
    version="0.1.0",
    author="Your Name",
    author_email="avinashmkamath@.gmail.com",
    description="A SCIM directory simulator and management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/scim-sim",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "faker",
    ],
    entry_points={
        "console_scripts": [
            "scim-sim=scim_sim.cli:main",
        ],
    },
) 
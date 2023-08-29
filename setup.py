"""
This is a setup script for the svarog_ctl module.
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="svarog_ctl",
    version="0.0.0",
    author="Tomek Mrugalski",
    author_email="spam.python@klub.com.pl",
    description="Automated satellite tracker that controls antenna rotors via rotctld",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gut-space/analog-noise-estimator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["orbit-predictor"],
    python_requires='>=3.6',
)

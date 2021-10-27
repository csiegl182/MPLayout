import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MPLayout",
    version="0.0.1",
    author="Christian Siegl",
    author_email="christian.siegl@gmail.com",
    description="High-level layout configuration for matplotlib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/csiegl182/MPLayout",
    project_urls={
        "Bug Tracker": "https://github.com/csiegl182/MPLayout/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"": ["mplstyles/*.mplstyle"]},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
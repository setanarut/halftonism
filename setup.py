from setuptools import setup


setup(
    name="halftonism",
    version="1.0.0",
    install_requires=["numpy>=1.26.1", "Pillow>=10.1.0", "pyora>=0.3.11"],
    python_requires=">=3.11.5",
    description="Artistic halftone generation library",
    url="https://github.com/setanarut/halftonism",
    scripts=["scripts/grad"],
    author="setanarut",
    license="GPL-3.0",
    packages=["halftonism"],
    classifiers=[
        "Programming Language :: Python :: 3.11.5",
    ],
    zip_safe=False,
)

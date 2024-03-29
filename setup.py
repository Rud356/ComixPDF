import setuptools
import comix_pdf

with open('README.md') as f:
    text = f.read()

with open("requirements.txt") as requirement_f:
    requirements = [line.strip() for line in requirement_f.readlines()]

with open("dev-requirements.txt") as dev_requirement_f:
    dev_requirements = [line.strip() for line in dev_requirement_f.readlines()]

setuptools.setup(
    name="comix_pdf",
    version=comix_pdf.__version__,
    author="Rud356",
    author_email="rud356github@gmail.com",
    description="Utility for converting images into pdf files",
    long_description=text,
    long_description_content_type="text/markdown",
    license="GPLv3",
    url="https://github.com/Rud356/ConfigFramework",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    python_requires=">=3.7, <3.10"
)
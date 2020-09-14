from setuptools import find_packages, setup

setup(
    name='rdamsc_userctl',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>= 3.6',
    install_requires=[
        'tinydb>=4',
        'dulwich',
        'passlib',
        'pytest',
        'coverage',
    ],
)

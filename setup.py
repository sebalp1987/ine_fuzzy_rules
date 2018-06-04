from setuptools import setup, find_packages

setup(
    name='fuzzy_rules',
    version='0.0.1',
    packages=find_packages('fuzzy_rules'),
    package_dir={'': 'fuzzy_rules'},
    include_package_data=True,
    install_requires=['fuzzywuzzy', 'unidecode', 'tqdm'],
    python_requires='3.6.1',
    package_data={'': ['*.txt', '*.csv']},


    author="Sebasti�n Mauricio Palacio",
    author_email="sebastian.mauricio.palacio@zurich.com",
    description="Detecting Logic Fuzzy Rules normalization",
    license="PSF",
    keywords="fuzzy rules, address, normalization",
    url="sebastian.mauricio.palacio@zurich.com",


)
import setuptools

setuptools.setup(
    name="covid_importer",
    version="0.0.1",
    description="imports covid data from Switzerland into a dataframe with cases, deaths and population per canton, agegroup and gender",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas>=1.0"
    ],
    python_requires=">=3.6"
)

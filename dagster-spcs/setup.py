from setuptools import find_packages, setup

setup(
    name="dagster_project",
    packages=find_packages(exclude=["dagster_project_tests"]),
    install_requires=[
        "dagster==1.7.*",
        "dagster-cloud",
        # "dagster-duckdb",
        # "geopandas",
        # "kaleido",
        "pandas",
        # "plotly",
        # "shapely",
        "snowflake-snowpark-python[pandas]",
        # "pandas",
        "python-dotenv"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest","dagit"]},
)

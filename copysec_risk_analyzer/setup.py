from setuptools import setup, find_packages

setup(
    name="copysec_risk_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "beautifulsoup4",
        "python-dotenv",
        "openai",
    ],
) 
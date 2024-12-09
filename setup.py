from setuptools import setup, find_packages

setup(
    name="copysec_risk_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'yfinance==0.2.33',
        'python-dotenv==1.0.0',
        'openai==1.3.5',
        'tqdm==4.66.1',
        'lxml==4.9.3'
    ]
) 
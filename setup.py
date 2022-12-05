from setuptools import setup

with open(file='README.md', mode='r') as readme_handler:
    long_description = readme_handler.read()

setup(
    name='cira',
    author='Julian Frattini',
    author_email='juf@bth.se',
    version='0.9.3',
    description='Implementation of the Causality in Requirements Artifacts (CiRA) functionality',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['nlp'],
    url='https://github.com/JulianFrattini/cira',
    python_requires='>=3.10',
    install_requires=[
        'numpy==1.23',
        'python-dotenv==0.20',
        'pytorch_lightning==1.7',
        'tabulate==0.8.10',
        'torch==1.12',
        'transformers==4.10',
        'uvicorn==0.18.3',
        'fastapi==0.85.0',
        'pydantic==1.10.2'
    ],
    extras_require = {
        'dev': [
            'pytest==7.1',
            'pytest-cov==3.0'
        ],
    },
)
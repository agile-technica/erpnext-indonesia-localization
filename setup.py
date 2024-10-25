from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in indonesia_taxes_and_charges/__init__.py
from indonesia_taxes_and_charges import __version__ as version

setup(
	name="indonesia_taxes_and_charges",
	version=version,
	description="Indonesia Taxes and Charges",
	author="Agile Technica",
	author_email="info@agiletechnica.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

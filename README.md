# Chaac 
Maya god of water and especially of rain.

# Description
This package extracts all the works published by publishers from any country, searched through the OpenAlex API, one of the main projects of OurResearch, which is an open and comprehensive catalog of academic articles, authors, institutions, publishers, etc.
## Install
```bash
$ pip install -i https://test.pypi.org/simple/ chaac
```
## Usage
The works of publishers from Luxembourg will be downloaded by entering the ISO 3166-1 alpha-2 country code. The output file (JSON) will be named OpenAlex-Luxembourg.
```bash
>>> chaac_run --country_codes="LU" --output="OpenAlex-Luxembourg"

```
Output
```bash
OpenAlex-Luxembourg.json
```
OpenAlex does not have information for all the entered ISO 3166-1 alpha-2 codes. For example, if the code for Bhutan ("BT") is entered, the OpenAlex API does not have any information on works related to that country.

Links:
* [Test pip page](https://test.pypi.org/project/Chaac/)
* Flake8 Tool For Style Guide Enforcement
  * https://flake8.pycqa.org/ 
  * https://peps.python.org/pep-0008/
* [GitHub actions](https://help.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions)

# First section is general, while second section is specific to this
# project.

################################################################################
## general
#
# Could be part of a general library of project management stuff
# shared across projects, which could be on pypi/anaconda (for
# pip/conda install), or maybe as a git submodule.

import glob
import platform
import os
import sys
import zipfile
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

DOIT_CONFIG = {'verbosity': 2}

miniconda_url = {
    "Windows": "https://repo.continuum.io/archive/Miniconda3-latest-Windows-x86_64.exe",
    "Linux": "https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh",
    "Darwin": "https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
}


# Download & install miniconda...Requires python already, so it might
# seem odd to have this. But many systems (including generic
# (non-python) travis and appveyor images) now include at least some
# system python, in which case this command can be used. But generally
# people will have installed python themselves, so the download and
# install miniconda tasks can be ignored.

def task_download_miniconda():
    url = miniconda_url[platform.system()]
    miniconda_installer = url.split('/')[-1]

    def download_miniconda(targets):
        urlretrieve(url,miniconda_installer)

    return {'targets': [miniconda_installer],
            'uptodate': [True], # (as has no deps)
            'actions': [download_miniconda]}


def task_install_miniconda():
    location = {
        'name':'location',
        'long':'location',
        'short':'l',
        'type':str,
        'default':os.path.abspath(os.path.expanduser('~/miniconda'))}

    miniconda_installer = miniconda_url[platform.system()].split('/')[-1]
    return {
        'file_dep': [miniconda_installer],
        'uptodate': [False], # will always run (could instead set target to file at installation location?)
        'params': [location],
        'actions': [
            'START /WAIT %s'%miniconda_installer + " /S /AddToPath=0 /D=%(location)s"] if platform.system() == "Windows" else ["bash %s"%miniconda_installer + " -b -p %(location)s"]
        }

def task_create_env():
    python = {
        'name':'python',
        'long':'python',
        'type':str,
        'default':'3.6'}

    env = {
        'name':'name',
        'long':'name',
        'type':str,
        'default':'test-environment'}

    return {
        'params': [python,env],
        'actions': ["conda create -y --name %(name)s python=%(python)s"]}


################################################################################
## specific to this project
#
# The aim would be to not have anything much here, but right now
# that's not easy because of awkward installation/specification of
# dependencies across projects.

def task_install_required_dependencies():
    return {'actions': ['conda install -y -q -c conda-forge param "bokeh>=0.12.10"']}

def task_install_test_dependencies():
    return {
        'actions': [
            'conda install -y -q -c conda-forge "holoviews>=1.9.0" pandas notebook flake8 pyparsing pytest',
            'pip install pytest-nbsmoke'],
        'task_dep': ['install_required_dependencies']
        }

def task_install_doc_dependencies():
    # would not need to exist if nbsite had conda package
    return {
        'actions': [
            'conda install -y -q -c conda-forge notebook ipython sphinx beautifulsoup4 graphviz selenium phantomjs',
            'pip install nbsite sphinx_ioam_theme'],
        'task_dep': ['install_test_dependencies']
        }

def task_lint():
    return {'actions': [
        'flake8 --ignore E,W parambokeh',
        'pytest --nbsmoke-lint examples/']}

def task_tests():
    return {'actions': [
        'pytest --nbsmoke-run examples/']}


def task_docs():
    # TODO: could do better than this, or nbsite could itself use doit
    # (providing a dodo file for docs, or using doit internally).
    return {'actions': [
        'nbsite_nbpagebuild.py ioam parambokeh ./examples ./doc',
        'sphinx-build -b html ./doc ./doc/_build/html',
        'nbsite_fix_links.py ./doc/_build/html',
        'touch ./doc/_build/html/.nojekyll',
        'nbsite_cleandisthtml.py ./doc/_build/html take_a_chance']}
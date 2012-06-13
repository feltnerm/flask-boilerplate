#!/usr/bin/env python

import binascii
import datetime
import os
import os.path
import platform
import urllib2
from pprint import pprint

from fabric.colors import *
from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *
from fabric.utils import *

"""
    fabfile

    Heavily inspired by: https://github.com/samuelclay/NewsBlur/blob/master/fabfile.py
"""


# ==============
# Color Printing
# ==============
def pblue(s, bold=False): 
    puts(blue(s,bold))
def pcyan(s, bold=False): 
    puts(cyan(s,bold))
def pgreen(s, bold=False): 
    puts(green(s, bold))
def pmage(s, bold=False): 
    puts(magenta(s,bold))
def pred(s, bold=False): 
    puts(red(s, bold))
def pwhite(s, bold=False): 
    puts(white(s, bold))
def pyellow(s, bold=False): 
    puts(yellow(s, bold))

@task
def penv():
    pblue("Current Environment:")
    pprint(env)


# ====================
# Environment Settings
# ====================

# Default
env.PROJECT_ROOT = os.path.dirname(__file__)
env.user = "mark"
env.roledefs = {
    'local': ['localhost'],
    #'web': ['web.uwplatt.edu']
    #'app': ['app.uwplatt.edu',
    #'dev': ['dev.uwplatt.edu'],
    #'ldap': ['ldap.uwplatt.ed'],
}

def server():
    env.PROJECT_ROOT = ""
    env.user = "" 
    env.key_filename = ""


@task
def web():
    server()
    env.roles = ['web']

@task
def app():
    server()
    env.roles = ['app']

@task
def dev():
    server()
    env.roles = ['dev']


# ========
# Settings
# ========
@task
def make_settings():
    """ Creates a new settings.py """
    
    settings = dict()

    # Prompt User for Settings
    pblue("Enter your environment settings.")
    settings['PRODUCTION'] = False
    if confirm(blue("Are these settings for a production server?")):
            settings['PRODUCTION'] = True
    puts('')
    if confirm(yellow("Verify everything looks correct?")):
        settings['SECRET_KEY'] = binascii.b2a_hqx(os.urandom(42))

        with cd(env.PROJECT_ROOT):
            with prefix('workon ' % env.PROJECT_VENV): 
                upload_template('settings.py.template', 
                        os.path.join(env.PROJECT_ROOT, 'settings.py'), 
                        context=settings, use_jinja=True, backup=False)

# ======================
# Environment Operations
# ======================
@task
def make_venv():
    if run('python3 --version', True):
        run('mkproject -p python2.7 %' % env.PROJECT_VENV)
    else:
        run('mkproject -p python2.7 webpi' % env.PROJECT_VENV)


# ===================
# Development / Debug
# ===================
@task
def console():
    local('ipython -i play.py')

@task
def less():
    local('lessc apps/static/less/style.less apps/static/css/style.css')

@task
def coffee():
    local('coffee -b --compile --output apps/static/js/ apps/static/coffee/*.coffee')

@task
def compile():
    less()
    coffee()

@task
def test():
    local('nosetest tests')


# ============
# Requirements
# ============
@task
def install_deps():
    """ Install dependencies depending on server type. """
    with prefix('source virtualenvwrapper.sh'):
        with prefix('workon webpi'):
            if confirm(magenta("Is this a production server?")):
                run('pip install -r requirements/prod.txt --use-mirrors')
            else:
                run('pip install -r requirements/dev.txt --use-mirrors')

@task
def freeze():
    pass

# ===============
# Version Control
# ==============
@task
def clone():
    pass
    #run('git clone git@bitbucket.org:feltnerm/operation-nomads.git %s' % env.PROJECT_ROOT)

@task
def pull():
    with cd(env.PROJECT_ROOT):
        run('git pull')

@task
@serial
def push():
    ''' Pushes local changes to master, and pulls them down to each server'''
    local('git push')
    with cd(env.PROJECT_ROOT):
        run('git pull')
@task
def status():
    s = local('git status --porcelain', True)
    if s:
        pyellow('Detected Changes to Branch', bold=True)
        puts(s)

# =====================
# Server Administration
# ====================


# ==========
# Migrations
# ==========


# ======
# Backups
# =======


# ===========
# Boilerplate
# ===========
@task
def boilerplate():
    """ Create a new project based on the boilerplate. """
    pgreen("Forging boilerplate.", bold=True)
    bp = dict()
    bp['SITE_NAME'] = prompt(magenta("Project Name: "))
    bp['PROJECT_ROOT'] = os.path.expanduser(os.path.join('~/Projects',bp['SITE_NAME']))
    if not confirm(green("%s okay for project root?" % bp['PROJECT_ROOT'])):
        bp['PROJECT_ROOT'] = prompt(magenta("Project Root: "))
    
    if not os.path.exists(bp['PROJECT_ROOT']):
        local('mkdir %s' % bp['PROJECT_ROOT'])
        local('cp -r %s/* %s' % (env.PROJECT_ROOT, bp['PROJECT_ROOT']))
        #upload_template('settings.py.template',
        #    bp['PROJECT_ROOT'],
        #    context=bp,
        #    use_jinja=True,
        #    backup=False
        #    )
    else:
        pred('Project already exists!')

# =========
# Bootstrap
# =========
@task
def bootstrap():

    pgreen("Bootstrappin' yer server!", bold=True)
    #make_venv()
    #install_deps()
    #pull()
    #init_postgres()
    #init_mongo()
    #make_settings()
    #init_migrate()
    
    #with cd(env.PROJECT_ROOT):
        #run('mkdir log/')
    

# ===============
# Setup :: Common
# ===============

# =========
# Utilities
# =========
@task
def clean():
    rmpyc()

@task
def pychecker():
    local('pychecker .')

@task
def pep8():
    """ Run PEP8 on my code. """
    puts("Checking python style")
    with cd(env.PROJECT_ROOT):
        local('pep8 .')
@task
def rmpyc():
    ''' Delete compiled python (.pyc) files. '''

    pwhite('Removing .pyc files.')
    local("find . -iname '*.pyc' -exec rm -v {} \;", capture=False)

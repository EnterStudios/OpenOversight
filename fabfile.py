from __future__ import with_statement
from fabric.api import env, local, run, sudo, cd, hosts, get
from fabric.context_managers import prefix
from fabric.contrib.console import confirm
import datetime, os
from os.path import expanduser
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())

basedir = os.path.abspath(os.path.dirname(__file__))

env.use_ssh_config = False

# Hosts
# env.hosts list references aliases in ~/.ssh/config or IP address. When using .ssh/config,
# fab will use the ssh keyfile referenced by the host alias, otherwise need to do what is
# being done in dev to assign env a key_filename

def development():
    env.environment = 'dev'
    env.hosts = '127.0.0.1'
    env.port = 2222
    env.user = 'vagrant'
    env.host = 'openoversight-dev'
    env.unprivileged_user = 'vagrant'
    env.venv_dir = '/home/vagrant/oovirtenv'
    env.code_dir = '/vagrant'
    env.backup_dir = '/home/vagrant/openoversight_backup'

def staging():
    env.environment = 'staging'
    env.user = 'root'
    env.hosts = 'staging.openoversight.lucyparsonslabs.com'
    env.unprivileged_user = 'nginx'
    env.venv_dir = '/home/nginx/oovirtenv/venv'
    env.code_dir = '/home/nginx/oovirtenv/venv/OpenOversight'
    env.backup_dir = '/home/nginx/openoversight_backup'

def production():
    env.environment = 'production'
    env.user = 'root'
    env.hosts = 'openoversight.lucyparsonslabs.com'
    env.unprivileged_user = 'nginx'
    env.venv_dir = '/home/nginx/oovirtenv'
    env.code_dir = '/home/nginx/oovirtenv/OpenOversight'
    env.backup_dir = '/home/nginx/openoversight_backup'

def deploy():
    with cd(env.code_dir):
        run('su %s -c "git fetch && git status"' % env.unprivileged_user)
        if confirm("Update to latest commit in this branch?", default=False):
            run('su %s -c "git pull"' % env.unprivileged_user)
            run('su %s -c "%s/bin/pip install -r requirements.txt"' % env.unprivileged_user, venv_dir)
            run('sudo systemctl restart openoversight')


def backup():
    run("su %s -c 'mkdir -p %s'" % (env.unprivileged_user, env.backup_dir))
    with cd(env.backup_dir):
        run('%s/bin/python %s/OpenOversight/db_backup.py' % (env.venv_dir, env.code_dir))
        run('mv backup.sql backup.sql_`date +"%d-%m-%Y"`')
        run('tar czfv backup.tar.gz backup.sql*')
        get(remote_path="backup.tar.gz", local_path="./backup/backup-%s-%s.tar.gz" % (env.environment, datetime.datetime.now().strftime('%Y%m%d-%H%m%d')))

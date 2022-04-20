from fabric.api import env, cd, prefix, run, task, shell_env
from fabric.colors import green


@task
def loc():

    env.host_string = 'localhost'
    env.user = 'vagrant'
    env.password = 'vagrant'
    env.path = "/home/vagrant/vish/src"
    env.reqs_path = "/home/vagrant/vish/src/requirements/local.txt"
    env.venv_path = "/home/vagrant/vish-env"
    env.venv_prefix = 'source %s/bin/activate' % env.venv_path
    env.dbname = 'vish'
    env.type = 'local'


@task
def prod():
    env.host_string = 'design.timvish.com'
    env.user = 'vish'

    env.path = "/home/vish/vish/src"
    env.reqs_path = "/home/vish/vish/src/requirements/production.txt"
    env.venv_path = "/home/vish/vish-env"
    env.venv_prefix = 'source %s/bin/activate' % env.venv_path

    env.dbname = "vish"
    env.type = 'production'


@task
def start(port=8000):
    manage_py('runserver_plus 0:%s' % port)


@task
def migrate(app=None):
    manage_py('migrate %s' % app) if app else manage_py('migrate')


@task
def shell():
    manage_py('shell_plus')


def manage_py(command):
    with cd(env.path), prefix(env.venv_prefix), shell_env(DJANGO_SETTINGS_MODULE='vish.settings.{}'.format(env.type)):
        run("%s/manage.py %s" % (env.path, command))


def is_local():
    return env.type == 'local'


def is_production():
    return env.type == 'production'


@task
def test_connection():
    """Test ability to run tasks"""
    run('uname -s')


@task
def restart():
    with cd(env.path), prefix(env.venv_prefix):
        if is_local():
            print 'Runserver will restart automatically on local'
        else:
            run("../vish.py -c " +
                "/home/vish/vish/conf/%s/ramona.conf restart" %
                env.type)


@task
def pull_code():
    with cd(env.path), prefix(env.venv_prefix):
        if is_local():
            run('git pull origin develop')
        elif is_production():
            run('git pull origin master')


def pip_install():
    with cd(env.path), prefix(env.venv_prefix):
        run("pip install -r %s" % env.reqs_path)


def collectstatic():
    if not is_local():
        manage_py("collectstatic --noinput -l")
    else:
        print 'No need to collectstatic on local'


def sync_database():
    manage_py("migrate")


@task
def deploy():
    """Deploy django"""

    print(green("Beginning Deploy: %s" % env.type))

    print(green("Pulling master from GitHub..."))
    pull_code()

    print(green("Installing requirements..."))
    pip_install()

    print(green("Collecting static files..."))
    collectstatic()

    print(green("Syncing the database..."))
    sync_database()

    print(green("Restarting server..."))
    restart()

    print(green("DONE!"))

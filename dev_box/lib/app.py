#!/usr/bin/env python
import click
import os
import inspect

try:
    script_path = os.path.abspath(os.path.dirname(__file__))
except NameError:  # ipython
    script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT_PATH = os.path.abspath(os.path.join(script_path, '..'))
os.chdir(ROOT_PATH)


stdout_prefix = '[{0}]'.format(ROOT_PATH)


@click.command()
def main():
    setup_configs__elasticsearch()
    setup_configs__kibana()


# TODO: move them to application folder
def setup_configs__elasticsearch():
    click.secho('{0} copying configs: elasticsearch'.format(stdout_prefix))
    os.system('cp -r lib/elasticsearch/config data/elasticsearch/')


def setup_configs__kibana():
    click.secho('{0} copying configs: kibana'.format(stdout_prefix))
    os.system('cp -r lib/kibana/config data/kibana/')


if __name__ == '__main__':
    main()

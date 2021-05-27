"""Module to run commands."""

import subprocess
import sys


class CommandParser():
    """Class to run commands."""

    def __init__(self):
        """Initialize class."""
        self.commands = {
            "run ru": "python3 -m CardGames ru",
            "run eng": "python3 -m CardGames eng",
            "run tests": "python3 -m unittest CardGames.code.test_games",
            "create docs": "cd docs && make html",
            "flake8": "flake8 ./CardGames/code",
            "pydocstyle": "pydocstyle ./CardGames/code",
            "pybabel update": "pybabel extract ./CardGames/code/* -o \
                ./CardGames/localization/CardGames.pot && \
                pybabel update -D CardGames -i \
                ./CardGames/localization/CardGames.pot -d \
                ./CardGames/localization/ -l eng && \
                pybabel update -D CardGames -i \
                ./CardGames/localization/CardGames.pot \
                -d ./CardGames/localization/ -l ru",
            "pybabel compile": "pybabel compile -d CardGames -i \
                ./CardGames/localization/eng/LC_MESSAGES/CardGames.po \
                -o ./CardGames/localization/eng/LC_MESSAGES/CardGames.mo && \
                pybabel compile -d CardGames -i \
                ./CardGames/localization/ru/LC_MESSAGES/CardGames.po -o \
                ./CardGames/localization/ru/LC_MESSAGES/CardGames.mo",
            "wheels": "python3 setup.py bdist_wheel && \
                pip3 install ./dist/CardGames*"
        }

    def run_command(self, command):
        """Run command."""
        if command in self.commands:
            subprocess.run(self.commands[command], shell=True)
        elif command == 'all':
            for command in [
                'wheels',
                'create docs',
                'pybabel update',
                'pybabel compile',
                'flake8',
                'pydocstyle'
            ]:
                subprocess.run(self.commands[command], shell=True)
        elif command == 'help':
            print("Shortcut: commands")
            for key, value in self.commands.items():
                print(
                    key + ':',
                    '\n\t'.join(' '.join(value.split()).split(' && '))
                )
            print("help: write all commands")
            print("all: setups project")
        else:
            print(
                "No such command;\n" +
                "Run with help options to see available commands"
            )


if __name__ == "__main__":
    CP = CommandParser()
    command = ' '.join([name for name in sys.argv[1:]])
    CP.run_command(command)

"""Setup script."""

import glob
import os

from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


def del_prefix(path):
    """Delete prefix path."""
    return os.path.relpath(path, "src")


packages = list(map(
    del_prefix,
    glob.glob("CardGames/resources/**/*", recursive=True))
)
locales = list(map(
    del_prefix,
    glob.glob("CardGames/localization/**/**/*", recursive=True))
)

setup(
    name='CardGames',
    version='0.1',
    author="Eugene Kolmagorov and Andrew Babichev",
    author_email="appleforopad@inbox.ru",
    description="Bleckjack, Fool and Queen games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AndrewBabichev/CardGames",

    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    packages=['CardGames', 'CardGames.code'],
    install_requires=[
        'playsound>=1.2.2',
        'numpy>=1.19.5',
        'Pillow>=8.2.0',
        'websocket_client>=1.0.1',
        'websockets==9.0.1',
        'vext.gi',
        'vext',
        'sphinx',
    ],
    entry_points={
        "console_scripts":
        [
            "cards = CardGames.__main__:main"
        ]
    },
    include_package_data=True,
    package_data={'': packages + locales}
 )

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='CardGames',
     version='0.1',
     scripts=['menu.py'] ,
     author="Deepak Kumar",
     author_email="appleforopad@inbox.ru",
     description="Bleckjack, Fool and Queen games",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/AndrewBabichev/CardGames",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )

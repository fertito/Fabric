from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "Fabric", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.Fabric',
      version=str(__version__),
      packages=['freecad',
                'freecad.Fabric'],
      maintainer="fertito",
      maintainer_email="fertito@fertito.net",
      url="https://foobar.com/me/coolWB",
      description="Fabric does something cool.",
      install_requires=['numpy',],
      include_package_data=True)

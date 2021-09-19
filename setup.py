import setuptools
import pkg_resources

pkg_resources.require("setuptools>45")
pkg_resources.require("setuptools_scm>=6.3.1")

if __name__ == "__main__":
    setuptools.setup()

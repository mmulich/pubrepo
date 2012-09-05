import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'lxml',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='pubrepo',
      version='0.0',
      description='pubrepo',
      long_description="",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pubrepo',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pubrepo:main
      [console_scripts]
      initialize_pubrepo_db = pubrepo.scripts.initializedb:main
      """,
      )

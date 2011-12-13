from setuptools import setup, find_packages
import sys, os

version = '0.9pre1'
shortdesc = 'node.ext.zodb'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='node.ext.zodb',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Utilities',
      ],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['node', 'node.ext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'node',
          'ZODB3',
          # -*- Extra requirements: -*
      ],
      extras_require = dict(
          test=[
                'interlude',
          ]
      ),
      tests_require=['interlude'],
      test_suite="node.ext.zodb.tests.test_suite"
      )

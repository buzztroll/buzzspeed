from setuptools import setup

setup(name='buzzspeed',
      version='0.1',
      description='Make graphs from speed test utput',
      url='http://github.com/buzztroll/buzzspeed',
      author='John Bresnahan',
      author_email='buzztroll@gmail.com',
      license='MIT',
      packages=['buzzspeed'],
      install_requires=[
          'docopt',
          'matplotlib',
      ],
      entry_points={
        'console_scripts': ['buzzspeed=buzzspeed.speedgraph:main'],
      },
      zip_safe=False)

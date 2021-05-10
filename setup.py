#!/usr/bin/env python3

from distutils.core import setup

setup(
  name = 'honeycomb-hive',
  packages = find_packages(),
  version = '0.1',
  license='MIT', 
  description = 'Second Layer service for Hive designed for non-webbased applications',
  author = 'Benjamin Flanagin',
  author_email = 'bflanagin@gmail.com',      
  url = 'https://github.com/VagueEntertainment/HoneyComb-redistributable', 
  download_url = 'https://github.com/VagueEntertainment/HoneyComb-redistributable/archive/v_01.tar.gz', 
  keywords = ['HIVE', 'LOCAL', 'SERVICE'],  
  install_requires=[    
          'hive',
          'websockets',
          'requests',
          'sqlite3',
          'bottle',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.9',
  ],
  python_requires='>=3.7',
)

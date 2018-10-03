""" Module for installing module as pip package """
import os
from setuptools import find_packages, setup
import sys

sys.path.insert(0, os.path.abspath(__file__))
from infocentre_data_manager import __version__

module_name = 'infocentre-data-manager'
module_dir_name = 'infocentre_data_manager'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name=module_name,
    version=__version__,
    packages=find_packages('.', exclude=['test']),
    include_package_data=True,
    license='MIT License',
    description='The HPV Information Centre data manager '
                'provide methods and utilities to upload scientific data '
                'from different sources and perform different (pluggable) '
                'data validation procedures to update the HPV Information '
                'Centre scientific databases.',
    long_description=README,
    url='https://www.hpvcentre.net',
    author='David Gómez',
    author_email='info@hpvcenter.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'sphinx-autoapi',
        'setuptools',
        'sphinx',
        'autoapi',
        'sphinxcontrib-websupport'
    ],
    entry_points={
        'data_manager.codecs': [
            'excel=infocentre_data_manager.plugins.codecs.excel:ExcelCodec',
            'old_excel=infocentre_data_manager.plugins.codecs.old_excel:OldExcelCodec',
            'mysql=infocentre_data_manager.plugins.codecs.mysql:MySQLCodec',
        ],
        'data_manager.data_validators': [
            'null=infocentre_data_manager.plugins.data_validators.null:NullValidator',
            'basic=infocentre_data_manager.plugins.data_validators.basic:BasicValidator',
            'type=infocentre_data_manager.plugins.data_validators.type:TypeValidator',
            'missing_values=infocentre_data_manager.plugins.data_validators.missing_values:MissingValuesValidator',
        ],
        'data_manager.semantic_types': [
            'integer=infocentre_data_manager.plugins.semantic_types.integer:IntegerType',
            'string=infocentre_data_manager.plugins.semantic_types.string:StringType',
            'iso=infocentre_data_manager.plugins.semantic_types.iso:IsoType',
        ],
    },
)

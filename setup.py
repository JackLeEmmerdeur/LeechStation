# from distutils.core import setup
# from sys import platform
from setuptools import setup

ir = [
	'ruamel.yaml >= 0.16.0',
	'pexpect >= 4.8.0'
]

setup(
	name='LeechStation',
	version='0.0.1',
	description='User-based SFTP-configuration for the linux SSH-Service',
	long_description='Adds a jailed user based SFTP-Configuration to an SSH-Server'
	author='Daniel Holgerson',
	author_email='jackleemmerdeur@googlemail.com',
	url='https://github.com/JackLeEmmerdeur/LeechStation',
	install_requires=ir,
	download_url='',
	keywords=['sftp', 'ssh', 'jailed', 'user', 'chroot', 'systemd'],
	packages=[
		'classes',
		'lib',
		'lang'
	],
	classifiers=[
		'Development Status :: 0.0.1 - Alpha',
		'Environment :: Console',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
		'Programming Language :: Python :: 3'
	]
)

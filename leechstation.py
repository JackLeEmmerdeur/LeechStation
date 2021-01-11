from classes.Yaml import Yaml
from classes.Station import Station


def main():
	# This enables you to add users only allowed
	# to use sftp, each only able to read/write
	# from/to their own jailed folder in
	#    /home/SFTP_USERS_DIR/USER
	# The script needs to modify the current
	# sshd_config file and is not tested at all
	# on different OS's.
	# Use at own risk!

	y = Yaml("./config.yaml")
	s = Station(y.get("sftp", "groupname"), y.get("sftp", "homepath"), y.get("app", "mode"))

	# - Alters /estc/ssh/sshd_config to use the above passed
	#   sftp-homepath as root for all sftp-users
	# - Creates said sftp-homepath
	# - Creates group for sftp-users
	# s.install()

	# Tries to remove the config-options added to /etc/ssh/sshd_config
	# in Station.install(). Not guaranteed to work.
	# s.uninstall()

	# Checks if LeechStation modifications are installed
	s.assert_installation()

	# Add an sftp-user
	# s.user_add("USERNAME", "PASSWORD")

	# Misc sftp-user functions
	# s.user_del("USERNAME")
	# s.user_change_password()
	# s.user_list()

	# Misc service-methods (start,stop,status)
	# s.sshstart()


if __name__ == "__main__":
	rc = 0
	try:
		exit(main())
	except SystemExit as e:
		exit(1)
	except Exception as e:
		print(e)
		exit(2)

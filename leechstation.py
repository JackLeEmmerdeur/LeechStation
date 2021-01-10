# from lib.syscmd import pexpectthis
# import pexpect
#
# c = pexpect.spawn("passwd naruto1")
# try:
# 	xoxo = c.expect("ein:", timeout=2)
# 	c.sendline("asdf")
# 	print(xoxo)
# 	# c.expect("ein:", timeout=2)
# 	# c.sendline("asdf")
# except pexpect.EOF:
# 	print("1")
# except pexpect.TIMEOUT:
# 	print("2")
# except:
# 	print("3")
from classes.Station import Station
from classes.Yaml import Yaml


def main():
	y = Yaml("./config.yaml")
	# s = Station(y.get("sftp", "groupname"), y.get("sftp", "homepath"), y.get("app", "mode"))

	# - Alters /etc/ssh/sshd_config to use the above passed
	#   sftp-homepath as root for all sftp-users
	# - Creates said sftp-homepath
	# - Creates group for sftp-users
	# s.install()

	# Tries to remove the config-options added to /etc/ssh/sshd_config
	# in Station.install(). Not guaranteed to work.
	# s.uninstall()

	# Checks if LeechStation modifications are installed
	# s.assert_installation()

	# Add an sftp-user
	# s.user_add("USERNAME", "PASSWORD")

	# Misc sftp-user functions
	# s.user_del("USERNAME")
	# s.user_change_password()
	# s.user_list()

	# Misc service-methods (start,stop,status,
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

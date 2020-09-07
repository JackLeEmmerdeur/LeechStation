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
	s = Station(y.get("sftp", "groupname"), y.get("sftp", "homepath"), y.get("app", "mode"))
	# s.user_del("naruto")
	# s.uninstall()
	# s.ssh_restart()
	s.install()
	s.assert_installation()
	s.user_add("naruto", "password123")
	s.user_list()

if __name__ == "__main__":
	rc = 0
	try:
		exit(main())
	except SystemExit as e:
		exit(1)
	except Exception as e:
		print(e)
		exit(2)

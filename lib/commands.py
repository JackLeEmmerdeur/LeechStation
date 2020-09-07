from plumbum import local

CSORT = local["sort"]
CCUT = local["cut"]
CMAKEDIR = local["mkdir"]
CADDUSER = local["useradd"]
CPASSWD = local["passwd"]
CCHOWN = local["chown"]
CCHMOD = local["chmod"]
CUSERDEL = local["userdel"]
CSYSTEMCTL = local["systemctl"]
CGROUPLIST = CCUT["-d:", "-f1", "/etc/group"] | CSORT
CGROUPDEL = local["groupdel"]
CGROUPADD = local["groupadd"]
CUSERLIST = CCUT["-d:", "-f1", "/etc/passwd"] | CSORT


def assert_retcode(retobj: tuple, errmsg: str) -> str:
	(retcode, stdout, stderr) = retobj
	if retcode != 0:
		print(stderr)
		raise Exception(errmsg)
	return stdout

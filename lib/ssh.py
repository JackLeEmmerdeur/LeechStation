from shutil import copy2
from lib.helpers import string_is_empty
from lib.commands import CSYSTEMCTL, assert_retcode
from pathlib import Path
import tempfile


def ssh_get_config_path() -> str:
	sshdconfigpath = Path("/etc/ssh/sshd_config")
	if not sshdconfigpath.exists():
		raise Exception("Bitte den OpenSSH Server installieren")
	return sshdconfigpath


def ssh_service(svcstatus: str) -> bool:
	retobj = CSYSTEMCTL[svcstatus, "ssh.service"].run(retcode=None)

	if svcstatus != "status":
		assert_retcode(retobj, "Konnte SSH Status nicht wechseln (" + svcstatus + ")")
	else:
		if len(retobj) > 1 or string_is_empty(retobj[1]):
			sout = retobj[1]
			started = False
			loaded = False
			for r in sout.split("\n"):
				if loaded is False and r.lower().find("loaded: loaded") > -1:
					loaded = True
				if started is False and r.lower().find("active: active (running)") > -1:
					started = True
			return loaded and started
		else:
			raise Exception("SSH Status konnte nicht ermittelt werden")


def ssh_service_try() -> bool:
	ssh_service("stop")
	if ssh_service("status") is True:
		return False
	ssh_service("start")
	if ssh_service("status") is False:
		return False
	ssh_service("stop")
	return ssh_service("status") is False


def ssh_config_get_userdir(sftpgroup: str) -> str:
	sshdconfigpath: Path = ssh_get_config_path()
	started = False
	foundgroup = False
	sftpuserdir = None

	with open(str(sshdconfigpath), "rt") as ssdconfig:
		for r in ssdconfig.readlines():
			if started is True:
				if r[0] != "\t":
					started = False
				if r.find("ChrootDirectory") > -1:
					sftpuserdir = r.strip()[15:].strip()

			if r.find("Match Group " + sftpgroup) > -1:
				started = True
				foundgroup = True

			if foundgroup is True and started is False:
				break

	if not string_is_empty(sftpuserdir):
		if sftpuserdir.endswith("%u"):
			return sftpuserdir[0:-3]
		else:
			return sftpuserdir
	else:
		print("No sftp-root-dir found in {}".format(sshdconfigpath))
	return sftpuserdir


def ssh_add_config(sftpgroup: str, sftpuserdir: Path):
	sshdconfig = Path("/etc/ssh/sshd_config")
	print("Ändere Konfiguration in: '" + str(sshdconfig) + "'")

	with open("/etc/ssh/sshd_config", "a+") as ssdconfig:
		ssdconfig.writelines([
			"Match Group " + sftpgroup + "\n",
			"\tForceCommand internal-sftp\n",
			"\tChrootDirectory " + str(sftpuserdir) + "/%u\n"
		])


def ssh_remove_config(sftgroup: str) -> bool:
	print("Suche Gruppe in SSH Config")
	sshdconfigpath: Path = ssh_get_config_path()
	foundgroup = False

	with tempfile.NamedTemporaryFile(mode="wt") as tmpfile:
		started = False
		with open(str(sshdconfigpath), "rt") as ssdconfig:
			for r in ssdconfig.readlines():
				if started is True:
					if r[0] != "\t":
						started = False
				else:
					if r.find("Match Group " + sftgroup) > -1:
						started = True
						foundgroup = True
					else:
						tmpfile.writelines([r])

		tmpfile.flush()

		if foundgroup is True:
			print("Gruppe wird aus '/etc/ssh/sshd_config' entfernt: '" + sftgroup + "'")
			print("Lege Sicherungskopie an: '/etc/ssh/sshd_config.old'")
			bakpath = Path("/etc/ssh/sshd_config.old")
			copy2(str(sshdconfigpath), str(bakpath))
			tmpfilepath = Path(tmpfile.name)
			sshdconfigpath.unlink()
			copy2(str(tmpfilepath), str(sshdconfigpath))

	if foundgroup is False:
		return True
	else:
		if ssh_service_try():
			print("SSH Konfiguration erfolgreich entfernt")
			return True
		else:
			print(
				"Etwas ist beim bearbeiten der SSH-Config falsch gelaufen. " +
				"Stelle Sicherung der SSH Konfiguration wieder her."
			)
			bakpath = Path("/etc/ssh/sshd_config.old")
			if not bakpath.exists():
				raise Exception("Konnte SSH-Config Sicherung nicht wieder herstellen!")

			sshdconfigpath.unlink()
			if sshdconfigpath.exists():
				raise Exception("Konnte fehlerhafte SSH Config nicht entfernen!")

			copy2(str(bakpath), str(sshdconfigpath))

			if not sshdconfigpath.exists():
				raise Exception("Konnte SSH-Config Sicherung nicht kopieren")

			print("Sicherung wiederhergestellt. Beende Programm!")
			return False
	return False

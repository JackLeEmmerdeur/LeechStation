from lib.commands import assert_retcode, CMAKEDIR, CADDUSER, CUSERLIST, CGROUPLIST, CCHOWN, CCHMOD, CUSERDEL
import pexpect
from pexpect.spawnbase import SpawnBase
from os import scandir, DirEntry
from pathlib import Path
from shutil import rmtree
from typing import Callable

PEXPECTERR = "String konnte nicht im Prozess-Ausgabestrom gefunden werden: "


def group_pexists(groupname: str) -> bool:
	retobj = CGROUPLIST.run(retcode=None)
	res = assert_retcode(retobj, "Konnte System-Gruppen nicht ermitteln")
	found = [row for row in res.split("\n") if row.strip().lower() == groupname]
	return found and len(found) > 0


def user_list(sftpuserdir: Path):
	if not sftpuserdir.exists():
		return None
	users = None
	with scandir(str(sftpuserdir)) as it:
		e: DirEntry
		for e in it:
			if e.is_dir():
				if users is None:
					users = []
				users.append(e.name)
	return users


def user_change_password(username: str, password: str):
	c = pexpect.spawn("passwd " + username)
	if pexpectthis(c, "ein:", password):
		if pexpectthis(c, "ein:", password):
			if pexpectthis(c, "erfolgreich"):
				return True
	return False


def user_create(username: str, password: str, sftpgroup: str) -> None:
	retobj = CADDUSER["-g",  sftpgroup, "-d", "/in", "-s", "/sbin/nologin", username].run(retcode=None)
	usrerr = "Konnte Benutzer nicht anlegen: '" + username + "'"
	assert_retcode(retobj, usrerr)
	if not user_exists(username):
		raise Exception(usrerr)
	user_change_password(username, password)


def user_folderexists(sftphome: Path, username: str) -> bool:
	return sftphome.joinpath(username).exists()


def user_folderdelete(sftphome: Path, username: str, rmtree_error_handler: Callable):
	p = sftphome.joinpath(username)
	if p.exists() and p.is_dir():
		rmtree(p, ignore_errors=False, onerror=rmtree_error_handler)


def user_delete(sftphome: Path, username: str, rmtree_error_handler: Callable) -> bool:
	print("Entferne Benutzer: '" + username + "'")
	b = False
	if user_exists(username):
		retobj = CUSERDEL[username].run(retcode=None)
		assert_retcode(retobj, "Konnte Benutzer nicht entfernen: '" + username + "'")

	if user_folderexists(sftphome, username):
		user_folderdelete(sftphome, username, rmtree_error_handler)


def user_exists(username: str) -> bool:
	retobj = CUSERLIST.run(retcode=None)
	res = assert_retcode(retobj, "Konnte Benutzerliste nicht ermitteln")
	found = [row for row in res.split("\n") if row.strip().lower() == username]
	return found and len(found) > 0


def user_sanitize_dir(sftphomepath: Path, username: str, sftpgroup: str):
	if sftphomepath is None or not sftphomepath.exists():
		raise Exception("SFTP Homepath existiert nicht")

	psub = sftphomepath.joinpath(username)

	if not psub.exists():
		print("SFTP Benutzer-Verzeichnis wird erstellt: '" + str(psub) + "' (root:root)")
		user_createfolder(psub, "root", "root", 755)
		if not psub.exists():
			raise Exception("Konnte nicht erstellt werden")

	psub_in = psub.joinpath("in")
	if not psub_in.exists():
		print("SFTP Benutzer-In-Verzeichnis wird erstellt: '" + str(psub_in) + "' (" + username + ":" + sftpgroup + ")")
		user_createfolder(psub_in, username, sftpgroup, 755)
		if not psub_in.exists():
			raise Exception("Konnte nicht erstellt werden")

	psub_out = psub.joinpath("out")
	if not psub_out.exists():
		print("SFTP Benutzer-Out-Verzeichnis wird erstellt: '" + str(psub_in) + "' (" + username + ":" + sftpgroup + ")")
		user_createfolder(psub_out, username, sftpgroup, 755)
		if not psub_out.exists():
			raise Exception("Konnte nicht erstellt werden")


def pexpectthis(pexpectobj: SpawnBase, expect_this: str, send_this: str=None) -> bool:
	try:
		i = pexpectobj.expect(expect_this, timeout=2)
		if send_this is not None:
			pexpectobj.sendline(send_this)
		return i == 0
	except pexpect.EOF:
		return False
	except pexpect.TIMEOUT:
		return False
	except:
		return False


def user_createfolder(sftphome: Path, username: str, groupname: str, permissions=0) -> None:
	pstr = str(sftphome)
	if sftphome.exists():
		print("Verzeichnis '" + pstr + "' existiert bereits")
	else:
		retobj = CMAKEDIR[pstr].run(retcode=None)
		assert_retcode(retobj, "Verzeichnis konnte nicht erstellt werden: '" + pstr + '"')
		retobj = CCHOWN[username + ":" + groupname, pstr].run(retcode=None)
		assert_retcode(
			retobj,
			"Benutzer/Gruppe für Verzeichnis konnten nicht vergeben werden: '" +
			pstr + " (" + retobj[2] if len(retobj) > 2 else retobj[1] + ")"
		)
		if permissions != 0:
			retobj = CCHMOD[str(permissions), pstr].run(retcode=None)
			assert_retcode(retobj, "Rechte für Verzeichnis konnten nicht vergeben werden: '" + pstr + "'")



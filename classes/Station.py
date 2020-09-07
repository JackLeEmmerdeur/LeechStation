from lib.syscmd import group_pexists, user_createfolder, user_exists, user_create, user_delete, user_list, \
	user_sanitize_dir, user_change_password
from lib.helpers import is_empty_sequence, string_is_empty
from lib.commands import CGROUPADD, CGROUPDEL, assert_retcode
from lib.ssh import ssh_remove_config, ssh_add_config, ssh_config_get_userdir, ssh_service_try, ssh_service
from pathlib import Path
from typing import Callable, Any
import shutil


class Station:

	sftpgroup: str = None
	sftphomedir: Path = None
	sshstarted: bool = False
	user_cachedlist_changed: bool = True
	user_cachedlist: str = None

	def __init__(self, sftpgroup: str, sftphomedir: str, mode: str):
		if string_is_empty(sftpgroup):
			raise Exception("SFTP-Gruppe wurde nicht angegeben")
		if string_is_empty(sftphomedir):
			raise Exception("SFTP-Homeverzeichnis wurde nicht angegeben")
		self.sftpgroup = sftpgroup
		self.sftphomedir = Path(sftphomedir)

	def on_rmtree_error(self, func: Callable, path: str, exc_info: Any):
		raise exc_info

	def sshstart(self):
		ssh_service("start")
		if ssh_service("status") is False:
			raise Exception("SSH Service konnte nicht gestartet werden")
		else:
			self.sshstarted = True

	def sshstop(self):
		ssh_service("stop")
		if ssh_service("status") is True:
			raise Exception("SSH Service konnte nicht gestoppt werden")
		else:
			self.sshstarted = False

	def sshrestart(self):
		Station.sshstop(self)
		Station.sshstart(self)

	def sshstatus(self) -> bool:
		return self.sshstarted

	def user_list(self):
		if self.user_cachedlist_changed:
			userlist = user_list(self.sftphomedir)
			if not is_empty_sequence(userlist):
				userlistlen = len(userlist)
				cachedlist = "SFTP Benutzer: " + str(userlistlen) + "\n"
				cachedlist += "==================\n"
				for index, u in enumerate(userlist):
					cachedlist += u
					if index < userlistlen - 1:
						cachedlist += "\n"
			else:
				cachedlist = "SFTP Benutzer: 0"
			self.user_cachedlist = cachedlist
			self.user_cachedlist_changed = False
		print(self.user_cachedlist)

	def user_del(self, username: str) -> bool:
		self.assert_installation()
		print("Entferne Benutzer: '" + username + "'")
		if user_exists(username) is False:
			print("Benutzer existiert nicht: '" + username + "'")
			return False
		else:
			self.user_cachedlist_changed = True
			return user_delete(self.sftphomedir, username, self.on_rmtree_error)

	def user_add(self, username: str, password: str):
		self.assert_installation()
		print("Lege Benutzer an: '" + username + "'")
		if user_exists(username):
			print("Benutzer existiert bereits: '" + username + "'")
		else:
			user_create(username, password, self.sftpgroup)
			self.user_cachedlist_changed = True
		user_sanitize_dir(self.sftphomedir, username, self.sftpgroup)

	def user_change_password(self, username: str, password: str):
		self.assert_installation()
		if not user_exists(username):
			print("Benutzer existiert nicht: '" + username + "'")
		else:
			if not user_change_password(username, password):
				print("Konnte Passwort nicht ändern für: '" + username + "'")
			else:
				print("Passwort erfolgreich geändert für: '" + username + "'")

	def assert_installation(self):
		if not self.check_installation():
			raise Exception("SSH Konfiguration fehlerhaft")

	def check_installation(self) -> bool:
		sftpuserdir = ssh_config_get_userdir(self.sftpgroup)
		if string_is_empty(sftpuserdir):
			return False
		if sftpuserdir != str(self.sftphomedir):
			return False
		p = Path(sftpuserdir)
		return p.exists()

	def uninstall(self):
		print("Deinstalliere eingeschränkte SFTP Umgebung")

		ssh_service_try()

		users = user_list(self.sftphomedir)

		if self.check_installation():
			rmres = ssh_remove_config(self.sftpgroup)
			if rmres is False:
				exit(3)

		if self.sftphomedir.exists():
			if not is_empty_sequence(users):
				for username in users:
					user_delete(self.sftphomedir, username, self.on_rmtree_error)

			print("Entferne SSH Home-Verzeichnis: '" + str(self.sftphomedir) + "'")
			shutil.rmtree(str(self.sftphomedir), ignore_errors=False, onerror=self.on_rmtree_error)

		if group_pexists(self.sftpgroup):
			print("Entferne Gruppe: '" + self.sftpgroup + "'")
			retobj = CGROUPDEL[self.sftpgroup].run(retcode=None)
			assert_retcode(retobj, "Konnte Gruppe nicht entfernen: '" + self.sftpgroup + "'")

		print("Fertig")

	def install(self):

		print("Installiere eingeschränkte SFTP Umgebung")
		print("Lege Gruppe an: '" + self.sftpgroup + "'")

		if group_pexists(self.sftpgroup):
			print("Gruppe existiert bereits: '" + self.sftpgroup + "'")
		else:
			retobj = CGROUPADD[self.sftpgroup].run(retcode=None)
			groupadderror = "Konnte Gruppe nicht hinzufügen: '" + self.sftpgroup + "'"
			assert_retcode(retobj, groupadderror)
			if not group_pexists(self.sftpgroup):
				raise Exception(groupadderror)

		print("Lege SFTP Home-Verzeichnis an: '" + str(self.sftphomedir) + "'")
		user_createfolder(self.sftphomedir, "root", "root")

		sshconfiguserdir = ssh_config_get_userdir(self.sftpgroup)

		if sshconfiguserdir is None or sshconfiguserdir != str(self.sftphomedir):
			print("Lege SSH Konfiguration an")
			ssh_add_config(self.sftpgroup, self.sftphomedir)

		if ssh_service_try() is False:
			print("Die Installation schlug fehl\nStarte Rollback!")
			self.uninstall()

		print("Fertig")

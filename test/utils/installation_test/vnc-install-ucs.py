#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""UCS installation via VNC"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os.path import dirname, join
from typing import Dict  # noqa: F401

from installation import VNCInstallation, build_parser, sleep, verbose
from vncdotool.client import VNCDoException
from yaml import safe_load


class UCSInstallation(VNCInstallation):

    def load_translation(self, language):  # type: (str) -> Dict[str, str]
        name = join(dirname(__file__), "languages.yaml")
        with open(name) as fd:
            return {
                key: values.get(self.args.language, "")
                for key, values in safe_load(fd).items()
            }

    @verbose("MAIN")
    def main(self):  # type: () -> None
        self.bootmenu()
        self.installer()
        self.setup()
        self.joinpass_ad()
        self.joinpass()
        self.hostname()
        self.ucsschool()
        self.finish()
        if self.args.second_interface:
            # TODO activate 2nd interface for ucs-kvm-create to connect to instance
            # this is done via login and setting interfaces/eth0/type, is there a better way?
            self.configure_kvm_network(self.args.second_interface)

    @verbose("GRUB")
    def bootmenu(self):  # type: () -> None
        """
        # Univention Corporate Server Installer
         Start with default settings
         Start with manual network settings
         Advanced options                      >
         Accessible dark contrast installer me >
         Help

        Automatic boot in 60 seconds...
        """
        if self.text_is_visible('Univention Corporate Server Installer'):
            if self.args.ip:
                self.client.keyPress('down')
            self.type('\n')

    @verbose("INSTALLER")
    def installer(self):  # type: () -> None
        # Sprache wählen/Choose language
        """
        # Select a language
        Choose the language to be used for the installed system. The UCS installer only supports English, French
        and German and will use English as fallback. Similar restrictions apply to the parts of the installed
        system which have not yet been localized.

        /Language:/
         ...
         English - English
         French - Français
         German - Deutsch
         ...

        [Screenshot]  [Go Back] [Continue]
        """
        for _ in range(3):
            self.client.waitForText('Select a language', timeout=self.timeout + 120, prevent_screen_saver=True)
            self.click_at(250, 250)
            self.type(self._['english_language_name'] + "\n")
            try:
                self.client.waitForText(self._['select_location'], timeout=self.timeout)
                break
            except VNCDoException:
                self.click_on('Go Back')

        """
        # Auswahl des Standorts
        Der hier ausgewählte Standort wird verwendet, um die Zeitzone zu setzen und auch, um zum Beispiel
        das System-Gebietsschema (system locale) zu bestimmen. Normalerweise sollte dies das Land sein, in
        dem Sie leben.
        Diese Liste enthält nur eine kleine Auswahl von Standorten, basierend auf der Sprache, die Sie
        ausgewählt haben. Wählen sie »weitere«, falls ihr Standort nicht aufgeführt ist.

        /Land oder Gebiet:/
         Belgien
         Deutschland
         Italien
         Lichtenstein
         Luxemburg
         Schweiz
         Österreich
         weitere
        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.click_at(250, 250)
        self.type(self._['location'] + "\n")

        # Access software for a blind person using a braile display
        # Die Sparchsynthesizer-Stimme konfigurieren

        """
        # Tastatur konfigurieren
        /Wählen Sie das Layout der Tastatur aus:/
         ...
         Deutsch
         ...
        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['select_keyboard'], timeout=self.timeout)
        self.click_at(250, 250)
        self.type(self._['us_keyboard_layout'] + "\n")

        # CD-ROM erkennen und einbinden
        # Debconf-Vorkonfigurationsdatei laden
        # Installer-Komponenten von CD laden

        # Netzwerk-Hardware erkennen
        sleep(60, "scan ISO and network")

        # Netzwerk einrichten
        if self.args.ip:
            self.network_setup()
            self.click_at(100, 320)
            sleep(1)

        """
        # Benutzer und Passwörter einrichten
        Sie müssen ein Passwort für »root«, das Systemadministrator-Konto, angeben. Ein bösartiger Benutzer
        oder jemand, der sich nicht auskennt und Root-Rechte besitzt, kann verheerenden Schaden anrichten.
        Deswegen sollte Sie darauf achten, ein Passwort zu wählen, das nicht einfach zu erraten ist. Es sollte
        nicht in einem Wörterbuch vorkommen oder leicht mir Ihnen in Verbindung gebracht werden können.
        Ein gutes Passwort enthält eine Mischung aus Buchstaben, Zahlen und Sonderzeichen und wird in
        regelmäßigen Abständen geändert.
        Das Passwort für den Superuser root muss mindestens 8 Zeichen umfassen.
        Hinweis: Sie werden das Passwort während der Eingabe nicht sehen.
        /Root-Passwort:/
         [...]
         [ ] Passwort im Klartext anzeigen
         Bitte geben Sie das root-Passwort nochmals ein, um sicherzustellen, dass Sie sich nicht vertippt
         haben.
        /Bitte geben Sie das Passwort zur Bestätigung nochmals ein:/
         [...]
         [ ] Passwort im Klartext anzeigen

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['user_and_password'], timeout=self.timeout)
        self.type("%s\t\t%s\n" % (self.args.password, self.args.password))

        if self.args.language == 'eng':
            """
            # Configure the clock
            If the desired time zone is not listed, then please go back to the step "Choose language" and select a country that uses the desired time
            zone (the country where you live or are located).
            /Select your time zone:
             Eastern <<
             Central
             Mountain
             Pacific
             Alaska
             Hawaii
             Arizona
             East Indiana
             Samoa

            [Bildschirmfoto]  [Zurück] [Weiter]
            """
            self.client.waitForText(self._['configure_clock'], timeout=self.timeout)
            # self.type(self._['clock'])
            sleep(1)
            self.type('\n')

        # Festplatte erkennen
        sleep(60, "disk.detect")
        self.disk_setup()

        """
        # Basissystem installieren
        """

        """
        # Paketmanager konfigurieren
        """

        """
        # Zusätzliche Software installieren
        """
        sleep(600, "disk.partition install")

        """
        # GRUB-Bootloader auf einer Festplatte installieren
        """

        """
        # Configure Univention System Setup
        """

        """
        # Installation abschließen
        /Installation abgeschlossen/
        Die Installation ist abgeschlossen und es ist an der Zeit, Ihr neues System zu starten. Achten Sie
        darauf, das Installationsmedium zu entfernen, so dass Sie das neue System starten statt einer
        erneuten Installation.

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['finish_installation'], timeout=1300)
        self.type('\n')
        sleep(30, "reboot")

    @verbose("DISK")
    def disk_setup(self):  # type: () -> None
        """
        # Festplatte partitionieren
        Der Installer kann Sie durch die Partitionierung einer Festplatte (mit verschiedenen Standardschemata)
        führen. Wenn Sie möchten, können Sie dies auch von Hand tun. Bei Auswahl der geführten
        Partitionierung können Sie die Einstellungen später noch einsehen und anpassen.
        Falls Sie eine geführte Partitionierung für eine vollständige Platte wählen, werden Sie gleich danach
        gefragt, welche Platte verwendet werden soll.
        /Partitionierungsmethode:/
         Geführt - vollständige Festplatte verwenden
         Geführt - gesamte Platte verwenden und LVM einrichten <<
         Geführt - gesamte Platte mit verschlüsseltem LVM
         Manuell

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['partition_disks'], timeout=self.timeout)
        sub = getattr(self, "_disk_%s" % (self.args.role,), self._disk_default)
        sub()

    def _disk_applianceLVM(self):  # type: () -> None
        # self.click_on(self._['entire_disk_with_lvm'])
        # LVM is the default so just press enter
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        Beachten Sie, dass alle Daten auf der Festplatte, die Sie wählen, gelöscht werden, jedoch nicht, bevor Sie bestätigt haben, dass Sie die
        Änderungen wirklich durchführen möchten.
        /Wählen Sie die zu partitionierende Festplatte:
         SCSI (0,0,0) (sda) - QEMU QEMU HARDDISC: 10.7 GB

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.type('\n')

        """
        # Festplatte partitionieren
        Für Partitonierung gewählt:

         SCSI (0,0,0) (sda) - QEMU QEMU HARDDISC: 10.7 GB

        Es gibt verschiedene Möglichkeiten, ein Laufwerk zu partitionieren. Wenn Sie sich nicht sicher sind, wählen Sie den ersten Eintrag.
        /Partitionierungsschema:/
         Alle Dateien auf eine Partition, für Anfänger empfohlen
         Separate /home-Partition

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.click_on(self._['all_files_on_partition'])
        self.type('\n')
        sleep(3)

        """
        # Festplatten partitionieren
        Bevor der Logical Volume Manager konfiguriert werden kann, muss die Aufteilung der Partitionen auf die Festplatte geschrieben
        werden. Diese Änderungen können nicht rückgängig gemacht werden.
        Nachdem der Logical Volume Manager konfiguriert ist, sind während der Installation keine weiteren Änderungen an der Partitionierung
        der Festplatten, die physikalische Volumes enthalten, erlaubt. Bitte überzeugen Sie sich, dass die Einteilung der Partitionen auf diesen
        Festplatten richtig ist, bevor Sie fortfahren.
        Die Partitionstabellen folgender Geräte wurden geändert:
         SCSI1 (0,0,0) (sda)
        /Änderungen auf die Speichergeräte schreiben und LVM einrichten?/
         (x) Nein
         ( ) Ja

        [Bildschirmfoto]  [Weiter]
        """
        self.client.keyPress('down')
        self.type('\n')

        """
        # Festplatte partitionieren
        Wenn Sie fortfahren, werden alle unten aufgeführten Änderungen auf die Festplatte(n) geschrieben. Andernfalls können Sie weitere
        Änderungen manuell durchführen.

        Die Partitionstabelle folgender Geräte wurden geändert:
         LVM VG vg_ucs, LV root
         LVM VG vg_ucs, LV swap_1
         SCSI1 (0,0,0) (sda)

        Die folgenden Partitionen werden formatiert:
         LVM VG vg_ucs, LV root als ext4
         LVM VG vg_ucs, LV swap_1 als Swap
         Partition 1 auf SCSI1 (0,0,0) (sda) als ext2

        /Änderungen auf die Festplatte schreiben?/
        (x) Nein
        ( ) Ja

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['continue_partition'], timeout=self.timeout)
        self.client.keyPress('down')
        self.type('\n')

    def _disk_applianceEC2(self):  # type: () -> None
        # Manuel
        self.click_on(self._['manual'])
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        Dies ist eine Übersicht über ihre konfigurierten Partitionen und Einbindepunkte. Wählen Sie eine Partition, um Änderungen vorzunehmen (Dateisystem,
        Einbindepunkte, usw.), freien Speicher, um Partitionen anzulegen oder ein gerät, um eine Partitionstabelle zu erstellen.
         Geführte Partitionierung
         iSCSI-Volumes konfigurieren

         SCSI (0,0,0) (sda) - 10.7 GB QEMU QEMU HARDDISK

         Änderungen an den Partitionen rückgängig machen
         Partitionierung beenden und Änderungen übernehmen

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.client.keyPress('down')
        self.client.keyPress('down')
        self.client.keyPress('down')
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        Sie haben ein komplettes Laufwerk zur Partitionierung angegeben. Wenn Sie fortfahren und eine neue Partitionstabelle anlegen,
        werden alle darauf vorhandenen Partitionen gelöscht.
        Beachten Sie, dass Sie diese Änderung später rückgängig machen können.
        /Neue, leere Partitionstabelle auf diesem Gerät erstellen?/
         (x) Nein
         ( ) Ja

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.keyPress('down')
        sleep(3)
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        Dies ist eine Übersicht über ihre konfigurierten Partitionen und Einbindepunkte. Wählen Sie eine Partition, um Änderungen vorzunehmen (Dateisystem,
        Einbindepunkte, usw.), freien Speicher, um Partitionen anzulegen oder ein gerät, um eine Paritionstabelle zu erstellen.
         Geführte Partitionierung
         Software-RAID konfigurieren
         Logical Volume Manager konfigurieren
         Verschlüsselte Datenträger konfigurieren
         iSCSI-Volumes konfigurieren

         SCSI (0,0,0) (sda) - 10.7 GB QEMU QEMU HARDDISK
          > pri/log 10.7 GB  FREIER SPEICHER

         Änderungen an den Partitionen rückgängig machen
         Partitionierung beenden und Änderungen übernehmen

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.click_on(self._['free_space'])
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        /Wie mit freiem Speicher verfahren:/
         Eine neue Partition erstellen
         Freien Speicher automatisch partitionieren
         Anzeigen der Zylinder-/Kopf-/Sektor-Informationen

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.type('\n')

        """
        # Festplatte partitionieren
        Die maximale Größe für diese Partition beträgt 10.7 GB.
        Tipp: »max« kann als Kürzel verwendet werden, um die maximale Größe anzugeben. Alternativ kann eine prozentuale Angabe (z.B.
        »20%«) erfolgen, um die Größe relativ zum Maximum anzugeben.
        /Neue Größe der Partition:/
         [10.7 GB]

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        # enter: ganze festplattengröße ist eingetragen
        self.type('\n')

        """
        # Festplatte partitionieren
        /Typ der neuen Partition:/
         Primär
         Logisch

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        # enter: primär
        self.type('\n')

        """
        # Festplatte partitionieren
        Sie bearbeiten Partition 1 auf SCSI1 (0,0,0) (sda). Auf dieser Partition wurde kein vorhandenes Dateisystem gefunden.
        /Partitionseinstellungen:
         Benutzen als: Ext4-Journaling-Dateisystem

         Einbindepunkt: /
         Einbindeoptionen: defaults
         Name: Keiner
         Reservierte Blöcke: 5%
         Typische Nutzung: standard
         Boot-Flag (Boot-fähig-Markierung): Aus

         Die Partition löschen
         Anlegen der Partition beenden

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.click_on(self._['boot_flag'])
        # enter: boot-flag aktivieren
        self.type('\n')
        sleep(3)
        self.click_on(self._['finish_create_partition'])
        self.type('\n')
        sleep(3)

        """
        # Festplatte partitionieren
        Dies ist eine Übersicht über ihre konfigurierten Partitionen und Einbindepunkte. Wählen Sie eine Partition, um Änderungen vorzunehmen (Dateisystem,
        Einbindepunkte, usw.), freien Speicher, um Partitionen anzulegen oder ein gerät, um eine Partitionstabelle zu erstellen.
         Geführte Partitionierung
         Software-RAID konfigurieren
         Logical Volume Manager konfigurieren
         Verschlüsselte Datenträger konfigurieren
         iSCSI-Volumes konfigurieren

         SCSI (0,0,0) (sda) - 10.7 GB QEMU QEMU HARDDISK
          > Nr. 1 primär 10.7 GB B f ext4 /

         Änderungen an den Partitionen rückgängig machen
         Partitionierung beenden und Änderungen übernehmen

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.click_on(self._['finish_partition'])
        self.type('\n')
        sleep(3)

        """
        # Festplatten partitionieren
        Sie haben keine Partition zur Verwendung als Swap-Speicher ausgewählt. Dies wird aber empfohlen, damit der Computer den
        vorhandenen Arbeitsspeicher effektiver nutzen kann, besonders wenn er knapp ist. Sie könnten Probleme bei der Installation
        bekommen, wenn Sie nicht genügend physikalischen Speicher haben.
        Wenn Sie nicht zum Partitionierungsmenü zurückkehren und eine Swap-Partition anlegen, wird die Installation ohne Swap-Speicher
        fortgesetzt.
        /Möchten Sie zum Partitionierungsmenü zurückkehren?/
          ( ) Nein
          (x) Ja

        """
        self.click_on(self._['no'])
        self.type('\n')

        """
        # Festplatte partitionieren
        Wenn Sie fortfahren, werden alle unten aufgeführten Änderungen auf die Festplatte(n) geschrieben. Andernfalls können Sie weitere
        Änderungen manuell durchführen.

        Die Partitionstabelle folgender Geräte wurden geändert:
         SCSI1 (0,0,0) (sda)

        Die folgenden Partitionen werden formatiert:
         Partition 1 auf SCSI1 (0,0,0) (sda) als ext4

        /Änderungen auf die Festplatte schreiben?
         (x) Nein
         ( ) Ja

        [Bildschirmfoto]  [Weiter]
        """
        self.client.waitForText(self._['continue_partition'], timeout=self.timeout)
        self.client.keyPress('down')
        self.type('\n\n')

    def _disk_default(self):  # type: () -> None
        self.click_on(self._['entire_disk'])
        self.type('\n')

        """
        # Festplatte partitionieren
        Beachten Sie, dass alle Daten auf der Festplatte, die Sie wählen, gelöscht werden, jedoch nicht, bevor Sie bestätigt haben, dass Sie die
        Änderungen wirklich durchführen möchten.
        /Wählen Sie die zu partitionierende Festplatte:/
          SCSI1 (0,0,0) (sda) - 10.7 GB QEMU QEMU HARDDISK

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        sleep(3)
        self.type('\n')

        """
        # Festplatte partitionieren
        Für Partitonierung gewählt:

         SCSI (0,0,0) (sda) - QEMU QEMU HARDDISC: 10.7 GB

        Es gibt verschiedene Möglichkeiten, ein Laufwerk zu partitionieren. Wenn Sie sich nicht sicher sind, wählen Sie den ersten Eintrag.
        /Partitionierungsschema:/
         Alle Dateien auf eine Partition, für Anfänger empfohlen
         Separate /home-Partition

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        sleep(3)
        self.type('\n')

        """
        # Festplatte partitionieren
        /Dies ist eine Übersicht über Ihre konfigurierten Partitionen und Einbindepunkte. Wählen Sie eine Partition, um
        Änderungen vorzunehmen (Dateisystem, Einbindepunkt, usw.), freien Speicher, um Partitionen anzulegen oder ein
        Gerät, um eine Partitionstabelle zu erstellen./
         Geführte Partitionierung
         Software-RAID konfigurieren
         Logical-Volume Manager konfigurieren
         Verschlüsselte Datenträger konfigurieren
         iSCSI-Volumes konfigurieren
         SCSI (0,0,0) (sda) - 21.5 GB QEMU QEMU HARDDISK
          > Nr. 1 primär  20.4 GB f ext4 /
          > Nr. 5 logisch  1.0 GB f swap Swap
         Änderungen an den Partitionen rückgängig machen
         Partitionierung beeenden und Änderungen übernehmen

        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.click_on(self._['finish_partition'])
        self.type('\n')

        """
        # Festplatte partitionieren
        Wenn Sie fortfahren, werden alle unten aufgeführten Änderungen auf die Festplatte(n) geschrieben.
        Andernfalls können Sie weitere Änderungen manuell durchführen.
        Die Partitionstabellen folgender Geräte wurden geändert:
         SCSI1 (0,0,0) (sda)
        Die folgenden Partitionen werden formatiert:
         Partition 1 auf SCSI1 (0,0,0) (sda) als ext4
         Partition 5 auf SCSI1 (0,0,0) (sda) als Swap
        /Änderungen auf die Festplatten schreiben?
         (x) Nein
         ( ) Ja
        [Bildschirmfoto] [Hilfe]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['continue_partition'], timeout=self.timeout)
        self.client.keyPress('down')
        self.type('\n')

    @verbose("NETWORK")
    def network_setup(self):  # type: () -> None
        """
        # Netzwerk einrichten
        Ihr System besitzt mehrere Netzwerk-Schnittstellen. Bitte wählen Sie die Schnittstelle (Netzwerkkarte),
        die für die Installation genutzt werden soll. Falls möglich, wurde die erste angeschlossene Schnittstelle
        ausgewählt.
        /Primäre Netzwerk-Schnittstelle:/
         enp1s0: Unbekannte Schnittstelle
         enp7s0: Unbekannte Schnittstelle

        [Bildschirmfoto]  [Zurück] [Weiter]
        """
        self.client.waitForText(self._['configure_network'], timeout=self.timeout)
        if not self.text_is_visible(self._['ip_address']):
            # always use first interface
            self.click_on(self._['continue'])
            sleep(60, "net.detect")

        if not self.args.ip:
            raise ValueError("No IP address")

        if self.text_is_visible(self._['not_using_dhcp']):
            """
            # Netzwerk einrichten
            /Die automatische Netzwerkkonfiguration ist fehlgeschlagen/
            Ihr Netzwerk benutzt möglicherweise nicht das DHCP-Protokoll. Des Weiteren könnte der DHCP-
            Server sehr langsam sein oder die Netzwerk-Hardware arbeitet nicht korrekt.
            [Bildschirmfoto] [Weiter]
            """
            self.type('\n')

            """
            # Netzwerk einrichten
            Hier können Sie wählen, die automatische DHCP-Netzwerkkonfiguration erneut zu versuchen (was
            funktionieren könnte, wenn Ihr DHCP-Server sehr langsam reagiert) oder das Netzwerk manuell zu
            konfigurieren. Manche DHCP-Server erfordern, dass der Client einen speziellen DHCP-Rechnernamen
            sendet, daher können Sie auch wählen, die automatische DHCP-Netzwerkkonfiguration mit Angabe eines
            Rechnernamens erneut zu versuchen.
            /Netzwerk-Konfigurationsmethode:/
             Autom. Konfiguration erneut versuchen
             Autom. Konfiguration erneut versuchen mit einem DHCP-Rechnernamen
             Netzwerk manuell einrichten
             Temporär eine Link-local-Adresse (169.254.0.0/16) verwenden

            [Bildschirmfoto]  [Zurück] [Weiter]
            """
            self.click_on(self._['manual_network_config'])
            self.type('\n')

        self.client.waitForText(self._['ip_address'], timeout=self.timeout)
        self.type(self.args.ip + "\n")
        if self.args.netmask:
            self.type(self.args.netmask)

        self.type('\n')
        self.client.waitForText(self._['gateway'], timeout=self.timeout)
        if self.args.gateway:
            self.type(self.args.gateway)

        self.type('\n')
        self.client.waitForText(self._['name_server'], timeout=self.timeout)
        if self.args.dns:
            self.type(self.args.dns)

        self.type('\n')

    def _network_repo(self):
        sleep(120, "net.dns")
        if self.text_is_visible(self._['repositories_not_reachable']):
            self.type('\n')
            sleep(30, "net.dns2")

    @verbose("SETUP")
    def setup(self):  # type: () -> None
        """
        # Domäneneinstellungen
        Bitte wählen Sie die Domäneneinstellungen.

          Erstellen einer neuen UCS-Domäne  Empfohlen
            Dieses System als erstes System einer neuen Domäne einrichten. Zusätzliche Systeme können der Domäne später beitreten.
          Einer bestehenden UCS-Domäne beitreten
            Wählen Sie diese Option, falls bereits mindestens ein UCS-System existiert.
          Einer bestehenden Microsoft Active-Directory-Domäne beitreten
            Dieses System wird Teil einer existierenden nicht-UCS Active-Directory-Domäne.

        [Weiter]
        """
        self.client.waitForText(self._['domain_setup'], timeout=self.timeout + 900)
        sub = getattr(self, "_setup_%s" % (self.args.role,))
        sub()

    def _setup_master(self):  # type: () -> None
        self.click_on(self._['new_domain'])
        self.go_next()
        self.client.waitForText(self._['account_information'], timeout=self.timeout)
        """
        # Kontoinformationen
        Geben Sie den Namen ihrer Organisation und eine E-Mail-Adresse für die Aktivierung von UCS ein.

          Name der Organisation
          E-Mail-Adresse zur Aktivierung von UCS (mehr Informationen)

        [Zurück] [Weiter]
        """
        self.type('home')
        self.go_next()

    def _setup_joined(self, role_text):  # type: (str) -> None
        self.click_on(self._['join_domain'])
        self.go_next()
        if self.text_is_visible(self._['no_dc_dns']):
            self.click_on(self._['change_settings'])
            self.click_on(self._['preferred_dns'])
            self.type(self.args.dns + "\n")
            self._network_repo()
            self.click_on(self._['join_domain'])
            self.go_next()

        self.client.waitForText(self._['role'])
        self.click_on(role_text)
        self.go_next()

    def _setup_backup(self):  # type: () -> None
        self._setup_joined('Backup Directory Node')

    def _setup_slave(self):  # type: () -> None
        self._setup_joined('Replica Directory Node')

    def _setup_member(self):  # type: () -> None
        self._setup_joined('Managed Node')

    def _setup_admember(self):  # type: () -> None
        self.click_on(self._['ad_domain'])
        self.go_next()
        self.client.waitForText(self._['no_dc_dns'], timeout=self.timeout)
        self.type('\n')
        self.click_on(self._['preferred_dns'])
        sleep(1)
        self.type(self.args.dns + "\n")
        self._network_repo()
        self.check_apipa()
        self.go_next()
        self.go_next()

    def _setup_applianceEC2(self):  # type: () -> None
        self.client.keyDown('ctrl')
        self.client.keyPress('w')  # Ctrl-Q
        self.client.keyUp('ctrl')
        """
        Close window and quit Firefox?
        [x] Confirm before quitting with Ctrl-Q
        [Cancel] [Quit Firefox]
        """
        if self.text_is_visible("Close windows and quit Firefox?", timeout=-3):
            self.type('\n')

        sleep(60, "ec2.finish")
        raise SystemExit(0)

    _setup_applianceLVM = _setup_applianceEC2

    def joinpass_ad(self):  # type: () -> None
        if self.args.role not in {'admember'}:
            return
        # join/ad password and user
        self.client.waitForText(self._['ad_account_information'], timeout=self.timeout)
        for _ in range(2):
            self.click_on(self._['address_ad'])
            self.type("\t")
            self.type(self.args.join_user + "\t", clear=True)
            self.type(self.args.join_password, clear=True)
            self.go_next()
            try:
                self.client.waitForText(self._['error'], timeout=self.timeout)
                self.type('\n')
                self.client.keyPress('caplk')
            except VNCDoException:
                break

    @verbose("JOIN")
    def joinpass(self):  # type: () -> None
        if self.args.role not in {'slave', 'backup', 'member'}:
            return
        self.client.waitForText(self._['start_join'], timeout=self.timeout)
        for _ in range(2):
            self.click_on(self._['hostname_primary'])
            sleep(5)
            self.type('\t')
            self.type(self.args.join_user + "\t", clear=True)
            self.type(self.args.join_password, clear=True)
            self.go_next()
            try:
                self.client.waitForText(self._['error'], timeout=self.timeout)
                self.type('\n')
                self.client.keyPress('caplk')
            except VNCDoException:
                break

    def hostname(self):  # type: () -> None
        """
        # Rechnereinstellungen
        Eingabe des Namens dieses Systems.

          Vollqualifizierter Domänenname: *
          LDAP-Basis *

        [Zurück] [Weiter]
        """
        if self.args.role == 'master':
            self.client.waitForText(self._['host_settings'], timeout=self.timeout)
        else:
            self.client.waitForText(self._['system_name'])

        self.type(self.args.fqdn, clear=True)
        if self.args.role == 'master':
            self.type('\t')

        self.go_next()

    def ucsschool(self):  # type: () -> None
        # ucs@school role
        if not self.args.school_dep:
            return

        self.client.waitForText(self._['school_role'], timeout=self.timeout)
        self.click_on(self._['school_%s' % (self.args.school_dep,)])
        self.go_next()

    @verbose("FINISH")
    def finish(self):  # type: () -> None
        """
        # Bestätigen der Einstellungen
        Bitte bestätigen Sie die gewählten Einstellungen, die nachstehend zusammengefasst sind.

          UCS-Konfiguration: Eine neue UCS-Domäne wird erstellt.
          Kontoinformationen
          * Name der Organisation: ...
          Domänen- und Rechnereinstellung
          * Vollqualifizierter Domänenname: ...
          * LDAP-Basis: ...
          [x] System nach der Einrichtung aktualisieren (mehr Informationen)
          Mit der Inbetriebnahme von UCS willigen Sie in unsere Datenschutzerklärung ein.

        [Zurück] [System konfigurieren]
        """
        self.client.waitForText(self._['confirm_config'], timeout=self.timeout)
        self.type('\n')
        sleep(self.setup_finish_sleep, "FINISH")

        """
        # UCS-Einrichtung erfolgreich
          UCS wurde erfolgreich eingerichtet.
          Klicken Sie auf /Fertigstellen/, um UCS in Betrieb zu nehmen.

        [Fertigstellen]
        """
        self.client.waitForText(self._['setup_successful'], timeout=2100)
        self.type('\t\n')
        sleep(10, "reboot")
        self.client.waitForText('univention', timeout=self.timeout)

    @verbose("KVM")
    def configure_kvm_network(self, iface):  # type: (str) -> None
        self.client.waitForText('corporate server')
        self.type('\n')
        sleep(3)
        self.type('root\n')
        sleep(5)
        self.type(self.args.password + "\n")
        self.type('ucr set interfaces-%s-tzpe`manual\n' % iface)
        sleep(30, "kvm.ucr")
        self.type('ip link set %s up\n' % iface)
        self.type('echo ')
        self.client.keyDown('shift')
        self.type('2')  # @
        self.client.keyUp('shift')
        self.type('reboot -sbin-ip link set %s up ' % iface)
        self.client.keyDown('shift')
        self.type("'")  # |
        self.client.keyUp('shift')
        self.type(' crontab\n')

    @verbose("NEXT")
    def go_next(self):  # type: () -> None
        self.click_at(910, 700)


def main():  # type: () -> None
    parser = ArgumentParser(
        description=__doc__,
        parents=[build_parser()],
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--language',
        choices=['deu', 'eng', 'fra'],
        default="deu",
        help="Select text language",
    )
    parser.add_argument(
        "--role",
        default="master",
        choices=["master", "backup", "slave", "member", "admember", "applianceEC2", "applianceLVM"],
        help="UCS system role",
    )
    parser.add_argument(
        "--school-dep",
        choices=["central", "edu", "adm"],
        help="Select UCS@school role",
    )

    group = parser.add_argument_group("Network settings")
    group.add_argument(
        "--ip",
        help="IPv4 address if DHCP is unavailable",
    )
    group.add_argument(
        "--netmask",
        help="Network netmask",
    )
    group.add_argument(
        "--gateway",
        help="Default router address",
        metavar="IP",
    )
    parser.add_argument(
        "--second-interface",
        help="configure second interface",
        metavar="IFACE",
    )
    args = parser.parse_args()

    if args.role in {'slave', 'backup', 'member', 'admember'}:
        assert args.dns is not None
        assert args.join_user is not None
        assert args.join_password is not None

    inst = UCSInstallation(args=args)
    inst.run()


if __name__ == '__main__':
    main()

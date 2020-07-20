# Badminton-App #
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/Adspectus/Badminton-App?style=flat-square&label=Version)](https://github.com/Adspectus/Badminton-App/releases)
[![GitHub issues](https://img.shields.io/github/issues/Adspectus/Badminton-App?style=flat-square&label=Issues)](https://github.com/Adspectus/Badminton-App/issues)
[![GitHub license](https://img.shields.io/github/license/Adspectus/Badminton-App?style=flat-square&label=License)](https://github.com/Adspectus/Badminton-App/blob/master/LICENSE)
[![Perl version](https://img.shields.io/static/v1?label=Perl&message=5&color=yellow&style=flat-square)](https://www.perl.org/)

[English](README.md)

Web-App für die Verwaltung von Trainingsterminen einer Badminton Gruppe

## Entstehungsgeschichte

Die App entstand mit dem Ziel, die Terminabsprache zwischen den Teilnehmern einer Badminton-Gruppe zu erleichtern und die Miete der benötigten Badmintonplätze dementsprechend anzupassen. Aufgrund von hoher Fluktuation war es oft unvorhersehbar, wieviele Teilnehmer zum wöchentlichen Trainingstermin erscheinen würden. Dadurch entstand manchmal die Situation, dass zu viele Plätze angemietet waren und bezahlt werden mussten oder dass zu viele Teilnehmer für die Anzahl gemieteter Plätze kamen und dadurch die individuelle Trainingszeit sehr kurz war.

Da die Spielstätte es ermöglicht, in ausreichender Zahl pauschal gebuchte Plätze kostenfrei bis zu einer bestimmten Frist vor dem Trainingstermin abzusagen, ging es darum, diese Frist für die Zu- oder Absagen der jeweiligen Teilnehmer verbindlich zu gestalten und verspätete Zu- oder Absagen zu sanktionieren.

Das hat allerdings auch zur Folge, dass die Zu- und Absagen in einfacher und transparenter Weise ermöglicht werden sollten. Absprachen per E-Mail oder Messenger erbrachten nicht die gewünschte Verbesserung, da sie zu unstrukturiert sind und durch Absprachen auf anderen Kanälen unterlaufen werden konnten. Zudem ist es für denjenigen, der fristgemäß Plätze stornieren (oder hinzubuchen) musste, eine Sisyphusarbeit, diese Zu- und Absagen zu verarbeiten und auch rückblickend nachvollziehbar die tatsächlich benötigte Anzahl Plätze zu buchen.

Hauptanforderung an eine App war es daher, eine einfache Möglichkeit für alle Teilnehmer zu schaffen, die eigene Teilnahme verbindlich zu- oder abzusagen, auch für einen längeren Zeitraum. Daraus und im Laufe der Zeit entstanden eine ganze Reihe von Nebenanforderungen, u.a.:

* Zur Herstellung von Verbindlichkeit sollte jeder Teilnehmer über ein Konto mit Passwort-Anmeldung (mit allen damit verbundenen Konsequenzen) verfügen.
* Nicht-Mitglieder sollten als Gäste teilnehmen können.
* Vermeidung von Karteileichen.
* Die Anwendung sollte auf jedem Endgerät funktionieren.
* Berichte über die Teilnahme, Kosten etc. zurück bis zum Vorjahr.

Die Anwendung entstand im Wesentlichen zwischen 2016 und 2017 mit einigen späteren Änderungen und Verbesserungen.

## Start

Die Anwendung ist als Web-App konstruiert, d.h. im Prinzip ist es eine Website, die auch auf kleineren Anzeigen (Mobilgeräte) funktioniert. Die Datenhaltung erfolgt über eine MySQL-Datenbank. Nachteil dieser Architektur ist, dass keine Offline-Verwendung möglich ist, d.h. die Anwendung lässt sich nur bei bestehender Internetverbindung bedienen.

### Voraussetzungen

* Webserver, z.B. Apache, mit CGI
* *Perl* 5
* MySQL mit aktiviertem Event Scheduler
* Zum Versenden von Mails: Externes SMTP-Gateway

### Installation

Unter der Vorraussetzung, dass ein Webserver, der *Perl*/CGI-Skripe ausführen kann, und ein MySQL-Server sowie *Perl* 5 installiert sind, folgende Schritte ausführen:

1. Dieses Repository in ein beliebiges Verzeichnis klonen.
2. Eine Konfiguration für den Webserver/virtuellen Host erstellen. Das Webroot-Verzeichnis muss auf das Verzeichnis `htdocs` zeigen. Eine Beispielkonfiguration (inklusive http->https Umleitung) für den pache Webserver enthält die Datei [badminton.conf](badminton.conf). Beachte, dass die dortigen Platzhalter &lt;IP&gt;, &lt;DOMAIN&gt;, &lt;INSTALLDIR&gt;, &lt;CERTFILE&gt; und &lt;KEYFILE&gt; mit entsprechenden echten Werten ersetzt werden müssen. &lt;INSTALLDIR&gt; ist das Verzeichnis aus Schritt 1.
3. Eine Datenbank sowie einen Datenbankbenutzer nebst Passwort erstellen. Zur Erstellung der Datenbank kann das SQL-Skript [badminton.sql](badminton.sql) verwendet werden. Der Datenbankbenutzer benötigt die folgenden Rechte: SELECT, INSERT, UPDATE, DELETE, EXECUTE, TRIGGER und CREATE TEMPORARY TABLES.
4. Benötigte *Perl*-Module installieren. Die meisten Module sind in einer Standardinstallation von *Perl* bereits enthalten. Um herauszufinden, welche Module nachinstalliert werden müssen, kann das *Perl*-Sript `CheckEnvironment.pl` verwendet werden, das über das Shell-Skript `CheckEnvironment.sh` aufzurufen ist. Jedes Modul, das nicht gefunden werden kann, hat eine Fehlermeldung zur Folge. Die fehlenden Module lassen sich entweder über die Software-Installation des Betriebssystems nachinstallieren, oder von [CPAN](https://www.cpan.org/) herunterladen. Ausnahme: `Website::Template` und `Website::Framework::Bootstrap` sind selbst geschriebene *Perl*-Module, die aus dem entsprechenden [Github-Repository](https://github.com/Adspectus/WebSite) installiert werden müssen.

### Konfiguration

Wenn die Vorrausetzungen erfüllt und die Anwendung wie oben beschrieben installiert ist, muss die Konfiguration der Anwendung durchgeführt werden. Diese efolgt mittels YAML-Dateien im Verzeichnis `config`. Die YAML-Dateien werden eingelesen und zu einer einzigen Konfiguration vereint. Die bestehenden Dateien enthalten die notwendigen Parameter, aber mit zum Teil leeren Werten. Entweder müssen diese Werte in den bestehenden Dateien angepasst werden, oder es wird eine einzige Datei `Local.yml` hinzugefügt, mit welcher alle in den anderen Dateien definierten Werte überschrieben werden können. Letztere Möglichkeit ist die empfohlene Variante und wird hier beschrieben.

Die `Local.yml` sollte mindestens folgende Parameter definieren:

```yaml
Environment: DEV
UI:
    Organisation: Sportfreunde Schiller
    Title: SF Schiller
DB:
    User: sfs_badminton
    Password: geheim
Email:
    Host: smtp.example.com
    User: max@sfs.de
    Password: geheim
    FromName: Sportfreunde Schiller Badminton-App
    FromMail: badminton-app@sfs.de
    ToName: Max Mustermann
    ToMail: max@sfs.de
```

Alle Parameter im Einzelnen:

#### `Environment`

Für Test- oder Entwicklungsinstallationen hier den Wert `DEV` oder `TEST` eingeben. Voreinstellung: `PROD`

#### `UI`

##### `Organisation`

Ein ausführlicher Name der Sportgruppe. Voreinstellung: `Badminton Sportgruppe`

##### `Title`

Ein kurzer Name der Sportgruppe. Voreinstellung: `Badminton`

##### `NextMatchdays`

Die Anzahl der zukünftigen Spieltermine, die dem Benutzer angezeigt werden. Voreinstellung: `8`

##### `LoginVarPrefix`

Ein Prefix für die Formfelder `username` und `password` zur Anmeldung. Voreinstellung: `bm_`

#### `DB`

##### `Host`

Die Adresse des MySQL-Servers. Voreinstellung: `localhost`

##### `Database`

Der Name der in Schritt 3 der Installation angelegten Datenbank. Voreinstellung: `badminton`

##### `User`

Der Name des in Schritt 3 der Installation angelegten Datenbankbenutzers. Voreinstellung: (leer)

##### `Password`

Das Passwort des in Schritt 3 der Installation angelegten Datenbankbenutzers. Voreinstellung: (leer)

#### `Email`

##### `Host`

Der Adresse des SMTP-Servers, welcher für den Email-Versand verwendet wird. Voreinstellung: (leer)

##### `SSL`

Verwende SSL für die Verbindung zum SMTP-Server. Voreinstellung: `1` (Ja)

##### `User`

Der Name des Benutzers für die Verbindung zum SMTP-Server. Voreinstellung: (leer)

##### `Password`

Das Passwort des Benutzers für die Verbindung zum SMTP-Server. Voreinstellung: (leer)

##### `FromName`

Der Absendername der von der App versendeten Mails. Voreinstellung: `Badminton-App`

##### `FromMail`

Die Absenderadresse der von der App versendeten Mails. Voreinstellung: (leer)

##### `ToName`

Der Empfängername der von der App versendeten Mails, wenn kein anderer Empfänger angegeben wird (zum Beispiel beim Testen). Voreinstellung: (leer)

##### `ToMail`

Die Empfängeradresse der von der App versendeten Mails, wenn kein anderer Empfänger angegeben wird (zum Beispiel beim Testen). Voreinstellung: (leer)

#### `Defaults`

##### `CourtsRented`

Die Anzahl der standardmäßig reservierten Plätze/Spielzeiten. Voreinstellung: `9`

#### `Settings`

##### `ParticipationDeadline`

Die Frist, bis zu der sanktionsfrei die Teilnahme zu- oder abgesagt werden kann in Sekunden vor dem Spieltermin. Voreinstellung: `91800` (25,5 Stunden)

## Verwendung

## Lizenz

[GNU General Public License v3.0](LICENSE)

## Danksagungen


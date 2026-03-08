# Internet of Things

Diese Repository enthält sowohl Übungen aus dem Studium als auch private Projekte.

## Inhalt
  - Studium
      - Verschiedene Übungen
      - Temperatursensor
      - MQTT Performance Auswertung
  - Private Projekte
      - Zeitentracker über API Zugriff auf Steampowered.com inklusive Darstellung im Browser
   
# Messaging im Internet der Dinge: Beispiele mit MQTT

## Abstract. 
Diese Ausarbeitung behandelt zwei durchgeführte Beispiele mit MQTT. 
Das erste Beispiel behandelt das Sammeln von Daten mittels eines ESP32 , welches mithilfe eines API Zugriffs Daten aus dem Internet sammelt und diese per MQTT an einem Raspberry Pi verschickt. Der Raspberry Pi verarbeitet diese Daten und speichert diese auf einer SQLite Datenbank und visualisiert diese auf einem Flask Webserver.
Das zweite Beispiel soll das Verhältnis zwischen Latenz und Quality of Service, Verbindungstyp (LAN oder WLAN), Nachrichtenfrequenz (1Hz oder 10Hz) und Datenmenge (76 Bytes oder 1KB) ermitteln.
Keywords: MQTT, Raspberry Pi, ESP32, Latency, API Access, SQLite, Quality of Service
##    1 Einleitung
Diese Ausarbeitung befasst sich mit dem MQTT Protokoll und möchte ein Einblick in die Kommunikation, Interaktion und Dienstgütestufen (QoS) mit MQTT bieten.
	Hierfür werden im folgenden Begriffe zu MQTT erläutert und diese anhand folgender zwei Beispiele veranschaulicht.
	Im ersten Beispiel werden Daten mithilfe eines ESP32 über einen API Zugriff aus dem Internet abgerufen und per MQTT an einen Raspberry Pi versendet, wo diese verarbeitet werden. Ziel dieses Beispiels ist es die zuvor manuell erfassten Daten zu automatisieren. 
	Das zweite Beispiel befasst sich mit der Performanz von MQTT im Hinblick auf die Latenz im Verhältnis zu den verschiedenen Parametern, darunter die verwendete QoS, der Verbindungstyp (LAN oder WLAN), Nachrichtenfrequenz (1Hz oder 10Hz) sowie der Datenmenge (76B oder 1KB).
##    2 Das MQTT Protokoll
Das MQTT Protokoll ist ein offenes und leichtgewichtetes Protokoll, das auf dem „Publish/Subscribe“ Prinzip funktioniert und somit ideal für Einsätze, wo geringe Rechenkapazität bzw. eingeschränkte Netzwerkkapazität herrscht, wie es im IoT üblich ist1.
###        2.1 Kommunikationsmodell – Publish/Subscribe
Das Publish/Subscribe Prinzip ermöglicht eine „One-To-Many“ Verteilung, bei der ein Produzent (Publisher) dieselbe Nachricht an mehrere Empfänger (Subscriber) versenden kann2, vorausgesetzt diese haben ein spezielles „Topic“ dazu abonniert3.

Publisher können mehrere Topics erstellen und Subscriber können mehrere Topics abonnieren und diese je nach Anwendungsfall weiterverarbeiten. 

Andernfalls lassen sich mehrere Daten in einem Topic zusammenfassen und die „Subscribers“ filtern je nach Anwendungsfall die relevanten Daten heraus. Dies erhöht die Nachrichtengröße und kann Konsequenzen in Form von Latenzen haben. Dazu in Kapitel 4.5 mehr.
Aus dem OASIS MQTT Standard werden Point-To-Point Kommunikationsmodelle nicht behandelt, so wird es diese Ausarbeitung ebenfalls nicht.
###        2.2 Dienstgüte
QoS 0 (at most once):
	Der Publisher sendet(published) genau ein mal eine Nachricht und erwartet keine Antwort vom Empfänger, ob diese angekommen ist oder nicht, daher kann der Empfänger die Nachricht genau ein mal oder gar nicht erhalten4.
QoS 1 (at least once):
	Der Publisher verschickt mehrmals dieselbe Nachricht und weist der Nachricht jedes mal eine andere ID zu. Der Publisher erwartet eine Antwort vom Subscriber, ob die Nachricht angekommen ist und schickt ständig weiter, bis eine “Acknowledgement”(PUBACK) vom Subscriber eingegangen ist.
Der Subscriber sendet nach Eingang der Nachricht eine PUBCAK mit derselben ID zurück und der Publisher löscht die Nachricht aus dem Speicher5.
QoS 2 (exactly once):
	QoS 2 erwartet einen zweifachen „Acknowledgement“ Prozess. Hierbei versieht der Publisher eine Nachricht mit einer ID und verschickt diese. Wird die Nachricht vom Subscriber empfangen, so sendet dieser eine PUBREC Nachricht mit derselben ID und „Reason Code“ zurück. Emfängt der Publischer die PUBREC Nachricht und ist diese der „Reason Code“ geringer als 0x80, so löscht dieser die ursprüngliche Nachricht und sendet eine PUBREL mit der ursprünglichen ID an den Subscriber. Der Subscriber löscht nach Ankunft der PUBREL die ID und sendet abschließend eine PUBCOMP an den Publisher6. 
###        2.3 Interaktionsmuster
Send and Forget:
	Ähnlich zu QoS 0 wird hier eine Nachricht verschickt und keine Antwort erwartet.
Request/Response:
	Ähnlich zu QoS 1 und QoS 2 wird hier eine Nachricht verschickt und eine Antwort erwartet, ob die Nachricht erfolgreich eingegangen ist ggf. kann auch eine Antwort zur Antwort erwartet werden, wie es in QoS 2 der Fall ist7.
###        2.4 Retain Flag
Die Retain Flag weist den MQTT Server an, die Nachricht unter dem zugehörigen Topic zu speichern. Wird eine neue Nachricht mit derselben Topic und einer Retain Flag empfangen, ersetzt diese die vorherige gespeicherte Nachricht. Neue Subscriber erhalten beim Abonnements des Topics automatisch die gespeicherte Nachricht, auch wenn der Publisher derzeit keine gesendet hat oder offline ist8.
##    3 Stundentracker
Dieses Beispiel basiert auf einem selbst erstellten Datensatz, der die täglichen Spielstunden eines Freundes im Spiel „Lost Ark“ dokumentiert. Die Motivation zur Erfassung begann im Februar 2023 während einer Diskussion, wo behauptet wurde er habe in letzter Zeit „gar nicht so viel gespielt“. Zu diesem Zeitpunkt hatte er bereits 2.324 Spielstunden gesammelt, obwohl das Spiel auf dem westlichen Markt erst am 11. Februar 2022 veröffentlicht wurde9.
	Aus Trotz und etwas Neugier begann daraufhin das systematische Tracking seiner Spielzeit. Ziel war es empirisch belegen zu können, dass er tatsächlich viel spielt – zumindest solange, bis er wieder einen Ausbildungsplatz gefunden hat. 
	Das Ziel dieses Beispiels ist es, die zuvor manuell erfassten Daten automatisch zu erfassen und visualisieren. Identifizierbare Informationen zur Person wurden aus dem Datensatz entfernt.
	Aus dem originalen Datensatz sind Stunden in gelb und weiß hinterlegter Farbe vorzufinden:
		Gelb: Durchschnittliche Stunden zwischen den tatsächlich erfassten Stunden.
		Weiß: Tatsächliche Stundenzahl.
Es ist Hinzuzufügen, dass ich keine eigenen Erfahrungen mit dem Spiel „Lost Ark“ habe, da ich es weder gespielt habe, noch vor habe zu spielen. Sämtliche Informationen beruhen auf Erzählungen oder ließen sich aus dem Verhalten meines Freundes erschließen, insbesondere wenn dieser für mehrere Wochen nicht mehr erreichbar war. Mir ist bewusst, dass dieser Teil meiner Recherche ungenügt, um genaue Aussagen über Spielverhalten oder Spielmuster zu treffen.
###        3.1 Aufbau
Zur Durchführung des Stundentrackers werden ein Raspberry Pi und ein ESP32 mit Internetzugang benötigt. Der Raspberry Pi muss in der Lage sein, verschiedene Aufgaben zu übernehmen, darunter das Erstellen, Beschreiben und Auslesen einer SQLite-Datenbank sowie das Hosten eines MQTT- und eines Flask-Webservers.
	Dazu müssen auf dem Raspberry Pi das Betriebssystem Raspberry Pi OS, Python 3.11.2, SQLite sowie die Bibliotheken Flask (v3.1.1) und paho-mqtt (v2.1.0) installiert sein.
	DbManager.py übernimmt sämtliche Aufgaben zu SQLite. MqttHost.py startet ein MQTT Server und speichert eingehende Nachrichten in der Datenbank. WebServer.py staretet einen Flask Webserver, der mithilfe von D3.js die Daten aus der Datenbank visualisiert.
Der ESP32 sammelt über einen API Zugriff auf Steam die Spielstunden und sendet diese mit QoS 1 und Retain Flag true an den Raspberry Pi.
###        3.2 Ergebnisse
	Durch den Zugriff auf die Steam API können nun Stundenzahlen in Dezimalstunden Genauigkeit erfasst werden, wie in Abb 3 und 4 zu sehen.


	Der Webserver visualisiert die Daten am Vorbild des Originaldatensatzes10. Dabei werden mithilfe des DbManager.py die Daten aus der Datenbank extrahiert.
	Aus Abbildung 5 sind lange horizontale Linien zu erkennen, diese zeigen die Perioden im Grundbestand an, die geschätzt werden mussten, weil ich das Tracken vergessen hatte oder fälschlicher Weise davon ausging, dass die Person eine Ausbildung angefangen hatte(August 2023 – Februar 2024).

Abbildung 6 zeigt die Verteilung der relativen Stunden über die Wochentage. Am Mittwoch findet ein sogenannter “Reset” statt, nach meinem Verständnis wird dabei der wöchentliche Content zurückgesetzt oder neue hinzugefügt, sodass diese wieder abgeschlossen werden können. Deutlich geringere Aktivität zeigen sich am Montag und Dienstag, was darauf zurückzuführen ist, dass sich der wöchentliche abschließbare Content „abgearbeitet“ wurde.



##    4 MQTT Performance Ergebnisse
Dieses Beispiel befasst sich mit der Performanz von MQTT mit Fokus auf die Latenz im Verhältnis zu den Parametern Quality of Service (QoS), Verbindungstyp (LAN oder WLAN), Nachrichtenfrequenz (1Hz oder 10Hz) und der Datenmenge (76B oder 1KB).
Die 0KB Data, in den Graphen, beziehen sich auf die Größe der „message“ Payload, die mit zufälligen UTF-8 Strings gefüllt ist.

###        4.1 Aufbau
Zur Durchführung des Performanztests werden ein Raspberry Pi und ein ESP32 mit Internetzugang benötigt. In diesem Versuchsaufbau fungieren beide Geräte als MQTT Host und Client. Der Raspberry Pi sendet eine Nachricht mit Zeitstempel, der ESP32 empfängt sie und sendet sie als Echo an den Raspberry Pi zurück. Dieser berechnet die Zeitdifferenz zwischen Versand und Empfang und speichert das Ergebnis in einer Datenbank.
	Die gesammelten Messwerte werden anschließend mit dem Skript extractDb.py jeweils in eine .csv Datei exportiert, um diese später auswerten zu können.
###        4.2 Methodik
Der Test basiert auf dem Code des Stundentrackers, verzichtet jedoch auf den Webserver, um Overhead zu reduzieren. Zudem kam es besonders bei größeren Datenmengen zu Nachrichtenverlusten und -korruptionen. Diese fehlerhaften Daten wurden nicht in die Analyse einbezogen, da diese die Latenzwerte verfälschten und die Auswertung der Grafiken erschwerten. Jeder Messdurchlauf pro Parameterkombination umfasst 100 Messungen.
	Die gemessenen Rohdaten sind sogenannte Round Trip Latenzen, d.h. die Nachrichten wurden vom Raspberry Pi an dem ESP32 verschickt und vom ESP32 wiederum an den Raspberry Pi zurückgeschickt. Um die tatsächliche Latenz (One Way), also nur den Hinweg, zu berechnen, wird der Round Trip Wert durch zwei geteilt. Dabei wird angenommen, dass die Latenzen in beiden Richtungen ungefähr gleich sind.
###        4.3 Ergebnisse
Im Folgenden werden die Ergebnisse als One Way Latenzen dargestellt. Besser skalierte Graphen und Tabellen können in der Abgabe oder online aufgerufen werden11.









###        4.4 Interpretation
QoS 0 und 1:
Hochfrequente Nachrichten (10 Hz) sind bei LAN-Verbindung des Raspberry Pi bei großen Datenmengen (1 KB) um den Faktor 1,45 und bei kleinen Datenmengen (76 Bytes) um den Faktor 1,83 besser als ihre niedrigfrequenten Gegenstücke.
Bei WLAN-Verbindung hingegen sind sie bei großen Datenmengen um den Faktor 0,62 schlechter, bei kleinen Datenmengen aber um den Faktor 2 besser.
QoS 2:
Bei gleichen Datengrößen und Verbindungsarten, aber unterschiedlichen Sendefrequenzen zeigt QoS 2 leichte Latenzverbesserungen(~20ms) bei 10Hz.
Alle Qualitätsstufen:
Bei gleichen Sendefrequenzen, aber kleinen Datenmengen verbessert sich die Latenz durchschnittlich um einen Faktor von etwa 2,8 im Vergleich zu großen Datenmengen, unabhängig vom Verbindungstyp.
###        4.5 Fazit
Die Qualitätsstufen 0 und 1 profitieren über LAN-Verbindung von hochfrequenten Nachrichten und weisen, unabhängig von Datengröße, deutlich geringere Latenzen als niedrigfrequente Nachrichten auf. Bei WLAN-Verbindung zeigen sich diese Vorteile nur bei kleinen Datenmengen, große Datenmengen führen bei Hochfrequenz zu höherer Latenz12.
	Qualitätsstufe 2 zeigt lediglich auf Hochfrequenz leichte Verbesserungen (10Hz), unabhängig von Datengröße und Verbindungstyp.
Insgesamt gilt, dass kleinere Datenmengen bei allen Qualitätsstufen zu einer durchschnittlich 2,8 fachen Verbesserung der Latenz führen können13.
	Aus den Grafiken ist zu entnehmen, dass bei niedrigfrequenten Nachrichten, unabhängig von der Datenmenge und Verbindungstyp, QoS 2 durchschnittlich zwar langsamer als die anderen Stufen ist, aber immer nah und ähnlich zu den anderen Qualitätstufen verläuft. Deutlich wird hier auch, dass QoS 1 und QoS 2 um eine Nachricht versetzt sind.
	Zusätzlich lässt sich entnehmen, dass hochfrequente Nachrichten bei kleinen Datensätzen, unabhängig vom Verbindungstyp, ähnliche Muster aufweisen. QoS 0 und QoS 1 zeigen hier ähnliche Muster, sind aber leicht auf der x-Achse versetzt. Möglicherweise entsteht die Verschiebung auf der x-Achse durch unterschiedliche Leistungsanforderungen je nach QoS Stufe.
##    5 Quellenverzeichnis
Abgabe: Laborjournal: Prüfungsleistung: Eigenes Beispiel – Spielstundentracker Kapitel 5 – Feature Showcase 

Abgabe: MQTT Ergebnisse [online]: https://docs.google.com/spreadsheets/d/1U5svWhpQfYZmJEpUOnv8KjgXw6beN9137WFBZl-ErH8/edit?usp=sharing (letzter Zugriff: 23.05.2025)

Gudenkauf, S. Vorlesungsfolie „Verteilte Anwendung - Message Queueing “

MQTT Version 5.0. Edited by Andrew Banks, Ed Briggs, Ken Borgendale, and Rahul Gupta. 07 March 2019. OASIS Standard. https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html (letzter Zugriff 20.05.2025)

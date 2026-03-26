# ─────────────────────────────────────────
# Duggirala
# German Daily Learning System
# ─────────────────────────────────────────

from fpdf import FPDF
import datetime
import pytz

WEEKDAYS = {0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag",
            4: "Freitag", 5: "Samstag", 6: "Sonntag"}
MONTHS = {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai",
          6: "Juni", 7: "Juli", 8: "August", 9: "September",
          10: "Oktober", 11: "November", 12: "Dezember"}

PRO_TIPS = [
    # Day 1-10: pronunciation & basics
    "Schreib jeden neuen Begriff laut auf und sprich ihn dreimal aus. Das Gehirn verknüpft Klang und Schrift am besten durch sofortige Wiederholung. Nutze auch dein Handy, um dich selbst aufzunehmen und zu vergleichen.",
    "Deutsche Vokale klingen reiner als englische: 'a' wie in 'Vater', 'o' wie in 'rot', 'u' wie in 'gut'. Übe jeden Vokal einzeln, bevor du ganze Wörter angehst. Dein Mund muss neue Positionen lernen.",
    "Das 'ü' ist wie ein englisches 'ee', aber mit gerundeten Lippen. Sag 'ee' und runde dann die Lippen. Das 'ö' geht genauso, aber mit einem 'e'-Anlaut. Täglich 2 Minuten reine Lautübung reicht aus.",
    "Das deutsche 'r' wird entweder gerollt (Zungenspitzen-R) oder gurgelt im Rachen. Das Rachen-R klingt moderner und ist einfacher. Übe 'rot', 'Regen', 'Rücken' täglich bis es automatisch kommt.",
    "Das 'ch' hat zwei Varianten: nach 'a', 'o', 'u', 'au' klingt es wie ein Kratzen (Buch, auch), nach anderen Vokalen wie ein leises Zischen (ich, nicht). Merkregel: dunkel vs. hell.",
    "Benutze Anki oder Quizlet, um neue Wörter mit Bild-Karten zu festigen. Spaced-Repetition-Systeme zeigen dir ein Wort genau dann wieder, bevor du es vergisst. 15 Minuten täglich schlägt 2 Stunden am Wochenende.",
    "Klebe Post-its auf Gegenstände in deiner Wohnung: 'der Tisch', 'die Tür', 'das Fenster'. Du siehst die Schilder Dutzende Male täglich ohne Aufwand. Nach einer Woche sind die Wörter automatisch gespeichert.",
    "Sprich beim Kochen oder Duschen auf Deutsch mit dir selbst. Beschreibe was du tust: 'Ich schneide die Zwiebel', 'Ich dusche mich'. Monologe bauen Sprechangst ab und festigen Satzmuster.",
    "Höre täglich mindestens 10 Minuten deutsches Audio, auch ohne alles zu verstehen. Dein Gehirn gewöhnt sich an den Rhythmus und die Melodie der Sprache. Podcasts wie 'Slow German' oder 'DW Langsam gesprochene Nachrichten' sind ideal.",
    "Erstelle ein Vokabelheft mit drei Spalten: Deutsch | Artikel | Englisch. Schreibe jedes neue Wort immer mit Artikel (der/die/das). Wer den Artikel von Anfang an lernt, muss ihn später nicht nachlernen.",
    # Day 11-20: grammar foundations
    "Im Deutschen hat jedes Substantiv ein grammatikalisches Geschlecht: maskulin (der), feminin (die), neutral (das). Es gibt keine perfekte Regel, aber Endungen helfen: '-ung' -> die, '-chen' -> das, '-er' (Beruf) -> der. Lerne den Artikel als Teil des Worts.",
    "Die vier deutschen Fälle (Nominativ, Akkusativ, Dativ, Genitiv) ändern den Artikel. Nominativ: der Mann ist da. Akkusativ: Ich sehe den Mann. Dativ: Ich gebe dem Mann Geld. Genitiv: Das Auto des Mannes. Fange mit Nominativ und Akkusativ an.",
    "Das deutsche Verb steht im Hauptsatz immer an zweiter Stelle. 'Heute gehe ich ins Kino.' Das Subjekt kann auch nach dem Verb kommen. Das nennt sich Verb-Zweit-Stellung und ist eine Kernregel.",
    "Trennbare Verben sind eine Besonderheit des Deutschen: 'aufmachen' -> 'Ich mache die Tür auf.' Das Präfix springt ans Satzende. Erkennbar an Präfixen wie: ab-, an-, auf-, aus-, ein-, mit-, vor-, zu-.",
    "Modalverben (können, müssen, dürfen, wollen, sollen, mögen) schicken das Infinitiv ans Satzende. 'Ich kann heute nicht kommen.' Lerne die Konjugationen dieser 6 Verben auswendig - du brauchst sie täglich.",
    "Die Negation mit 'nicht' steht vor dem Adjektiv oder am Satzende: 'Das ist nicht gut.' / 'Ich komme nicht.' Bei Nomen nimmst du 'kein': 'Ich habe kein Geld.' Merke: nicht = not, kein = no.",
    "Adjektive vor Nomen ändern ihre Endung je nach Artikel und Fall. 'Ein guter Mann', 'eine gute Frau', 'ein gutes Kind'. Das klingt komplex, aber im Alltag reichen dir drei Muster für 80% der Fälle.",
    "Pluralformen im Deutschen folgen keiner einheitlichen Regel. Lerne jedes Nomen mit seinem Plural: 'der Mann - die Männer', 'das Kind - die Kinder'. Häufige Muster: -e, -er, -en, -nen, -s (bei Fremdwörtern).",
    "Perfekt ist die häufigste Vergangenheitsform in der gesprochenen Sprache: 'haben/sein + Partizip II'. Ich habe gegessen. Ich bin gegangen. Bewegungsverben und Zustandsveränderungen nehmen 'sein', alle anderen 'haben'.",
    "Die Wortstellung im Nebensatz ist anders: das Verb steht am Ende. 'Ich weiß, dass er heute kommt.' Das 'kommt' springt ans Ende. Bei Modalverben im Nebensatz: Infinitiv + Modalverb ganz am Ende.",
    # Day 21-30: vocabulary building
    "Lerne Wörter in semantischen Feldern: alle Küchengeräte, alle Transportmittel, alle Emotionen. Gruppenlernen erleichtert das Abrufen, weil verwandte Wörter zusammen im Gedächtnis gespeichert werden.",
    "Wortbildung ist im Deutschen besonders produktiv. Aus 'Arbeit' entstehen: Arbeiter, Arbeiterin, arbeitslos, Arbeitgeber, Arbeitnehmer, Arbeitszimmer. Lerne Präfixe (un-, ver-, be-) und Suffixe (-ung, -heit, -keit, -schaft).",
    "Komposita (zusammengesetzte Wörter) sind typisch deutsch: Donaudampfschifffahrtsgesellschaft ist ein Extrembeispiel, aber 'Hausaufgabe', 'Fußgänger', 'Krankenhaus' begegnen dir täglich. Das letzte Glied bestimmt den Artikel.",
    "Falsche Freunde (false friends) sind Wörter, die dem Englischen ähneln, aber anderes bedeuten. 'Das Gift' = poison (nicht gift). 'Der Chef' = boss (nicht chef). 'Bekommen' = to get (nicht become). Lerne diese Liste aktiv.",
    "Kognaten (echte Verwandte) erleichtern das Lernen: 'Haus' = house, 'Wasser' = water, 'Gras' = grass, 'Arm' = arm. Viele deutsche Wörter haben englische Entsprechungen aus dem Germanischen. Nutze diese Brücken bewusst.",
    "Erstelle Wortfamilien-Mindmaps: In der Mitte 'reisen', drumherum 'die Reise', 'der Reisende', 'reiselustig', 'Reisepass', 'Reiseziel'. Visuelle Strukturen helfen dem Langzeitgedächtnis.",
    "Lies täglich einen kurzen deutschen Text auf deinem Niveau. Schlage nicht jedes Wort nach, sondern versuche den Sinn aus dem Kontext zu erschließen. Das trainiert echte Lesekompetenz und ist die schnellste Weg zum Vokabelwachstum.",
    "Idiome und feste Ausdrücke machen die Sprache lebendig: 'Ich drücke dir die Daumen' (I keep my fingers crossed), 'Das geht mir auf den Keks' (That gets on my nerves). Lerne täglich einen Ausdruck.",
    "Zahlen sind Werkzeuge - nicht nur Vokabeln. Rechne auf Deutsch: zwanzig minus sieben ist dreizehn. Sage Telefonnummern laut. Nenne Preise beim Einkaufen auf Deutsch. Zahlen müssen automatisch abrufbar sein.",
    "Führe ein Sprachlerntagebuch auf Deutsch. Schreibe 3-5 Sätze täglich über deinen Tag. Fehler sind erwünscht - sie zeigen, wo du noch Lücken hast. Nach 30 Tagen siehst du deinen Fortschritt schwarz auf weiß.",
    # Day 31-40: listening & speaking
    "Schau deutsche YouTube-Videos mit deutschen Untertiteln - nicht englischen. So verknüpfst du Aussprache und Schriftbild. Anfänger starten mit langsam gesprochenen Videos, Fortgeschrittene mit normaler Gesprächsgeschwindigkeit.",
    "Die 'Shadowing'-Technik: Sprich exakt gleichzeitig mit einem deutschen Sprecher nach. Das klingt absurd, aber es ist die schnellste Methode, Rhythmus, Intonation und Aussprache zu verbessern. 5 Minuten täglich reichen.",
    "Finde einen Tandempartner auf Tandem-App oder HelloTalk: Du sprichst 30 Minuten Deutsch, dein Partner 30 Minuten Englisch. Echte Gespräche ersetzen keine App der Welt. Schon ein Gespräch pro Woche macht einen Unterschied.",
    "Sätze auswendig lernen ist effektiver als einzelne Wörter. 'Können Sie das bitte wiederholen?', 'Ich verstehe das nicht.', 'Wie sagt man ... auf Deutsch?' Diese Sätze öffnen dir jeden Dialog.",
    "Lerne die deutschen Modalpartikeln: 'doch', 'ja', 'halt', 'eben', 'mal'. Sie sind schwer zu übersetzen, aber unverzichtbar für natürliches Deutsch. 'Komm doch mit!' klingt viel einladender als 'Komm mit!'",
    "Mache täglich 5-Minuten-Monologe zu einem Bild oder Foto. Beschreibe was du siehst, was die Personen fühlen, was gleich passieren könnte. Diese Übung trainiert spontanes Sprechen ohne Skript.",
    "Hör deutschen Nachrichten-Radio (Deutschlandradio, WDR) im Hintergrund. Selbst wenn du nicht aktiv zuhörst, gewöhnt sich dein Gehirn an authentische Sprache. Dein passiver Wortschatz wächst unbewusst.",
    "Nimm an Online-Deutschkursen auf Coursera oder dem Goethe-Institut teil. Strukturierte Kurse geben dir einen klaren Lernpfad und professionelles Feedback. Viele sind kostenlos oder günstig.",
    "Sprich Dialoge aus Büchern oder Filmen laut nach. Schlüpfe in eine Rolle - sei der Detektiv, sei die Krankenschwester. Rollenspiele bauen Hemmschwellen ab und machen das Lernen unterhaltsamer.",
    "Erstelle kurze Voicemail-Nachrichten auf Deutsch für dich selbst. Höre sie am nächsten Tag ab und prüfe Aussprache und Natürlichkeit. Dieser Trick simuliert echte Kommunikation ohne sozialen Druck.",
    # Day 41-50: grammar intermediate
    "Der Konjunktiv II wird im Deutschen für höfliche Bitten verwendet: 'Könnte ich bitte...?', 'Würden Sie...?', 'Ich hätte gerne...'. Lerne mindestens diese drei Formen - sie machen dich sofort höflicher und natürlicher.",
    "Reflexive Verben sind im Deutschen häufiger als im Englischen: 'sich waschen', 'sich freuen', 'sich vorstellen'. Das Reflexivpronomen (mich/dich/sich/uns/euch) muss zum Subjekt passen. Lerne sie immer mit 'sich'.",
    "Genitivkonstruktionen: 'Das Auto meines Vaters' (des Vaters). Im Alltag hört man aber auch Dativ: 'Das Auto von meinem Vater.' Der Genitiv klingt formeller. Erkenne ihn bei Texten, benutze im Gespräch ruhig Dativ.",
    "Relativsätze verbinden Informationen: 'Der Mann, der dort steht, ist mein Kollege.' Das Relativpronomen richtet sich nach Geschlecht und Kasus des Bezugsnomens. Übe täglich einen Relativsatz zu formulieren.",
    "Präpositionen regieren bestimmte Fälle: 'mit' -> immer Dativ, 'durch/für/gegen/ohne/um' -> immer Akkusativ, 'an/auf/hinter/in/neben/über/unter/vor/zwischen' -> Akkusativ (Bewegung) oder Dativ (Ort).",
    "Passiv: 'Der Brief wird geschrieben.' (Präsens Passiv). 'Der Brief wurde geschrieben.' (Präteritum Passiv). Passiv schiebt die Handlung in den Vordergrund, der Täter wird unwichtig. Im Deutschen häufig in formellen Texten.",
    "Infinitivkonstruktionen mit 'zu': 'Es ist wichtig, deutsch zu lernen.' 'Ich habe Lust, heute spazieren zu gehen.' Der Infinitiv mit 'zu' steht am Ende der Ergänzung. Bei trennbaren Verben: 'aufzumachen'.",
    "Der Unterschied zwischen 'seit' und 'vor': 'seit' = since/for (ongoing), 'vor' = ago (past, completed). 'Ich lerne seit drei Monaten Deutsch' (ongoing). 'Ich habe vor einem Jahr begonnen' (point in past).",
    "Wechselpräpositionen (an, auf, hinter, in, neben, über, unter, vor, zwischen) stehen mit Akkusativ für Bewegung und Dativ für Ort/Lage. Frage dich: Wohin? -> Akkusativ. Wo? -> Dativ. Das ist die einfachste Merkhilfe.",
    "Das Futur I ('werden + Infinitiv') wird im Deutschen selten für Zukunft genutzt - meist nimmt man Präsens + Zeitangabe: 'Ich gehe morgen ins Kino.' 'Werden' bedeutet oft Vermutung: 'Er wird wohl schlafen.'",
    # Day 51-60: A2 to B1 transition
    "Auf dem Weg zu B1 musst du Textsortenkenntnis aufbauen: E-Mails, Berichte, Bewerbungen haben je eigene Formulierungen. Lerne mindestens 3 Musterbriefe auswendig - der Rest lässt sich ableiten.",
    "B1-Niveau bedeutet: Du kannst über vertraute Themen sprechen, Reisen planen, einfache Meinungen äußern. Teste dich mit Übungsaufgaben vom Goethe-Institut (kostenlos online). Setze dir ein Prüfungsdatum.",
    "Lies täglich die Kindernachrichten auf 'logo!' (ZDF) oder 'Nachrichten leicht' (DW). Diese Texte sind auf B1-Niveau geschrieben, aber inhaltlich erwachsen. Ideale Brücke zwischen Lernen und echtem Sprachgebrauch.",
    "Verbesserung Deines Schreibstils: Nutze Konnektoren wie 'außerdem', 'jedoch', 'deshalb', 'trotzdem', 'obwohl'. Sie verbinden Sätze logisch und signalisieren B1/B2-Kompetenz beim Prüfer.",
    "Übe das Zusammenfassen von Texten: Lies 2-3 Absätze und schreibe sie in 3-4 Sätzen zusammen. Diese Fähigkeit ist zentral für die B1/B2-Prüfung und trainiert sowohl Lese- als auch Schreibkompetenz.",
    "Kaufe das Übungsbuch zur Goethe-Zertifikat B1 Prüfung. Mach täglich eine Aufgabe. Die Prüfungsformate (Hörverstehen, Lesen, Schreiben, Sprechen) sind trainierbar - je mehr du übst, desto sicherer wirst du.",
    "Hörverstehen verbessert sich durch aktives Zuhören: Notiere beim ersten Durchgang nur Schlüsselwörter, beim zweiten ergänze Details. Dieser Two-Pass-Ansatz ist die Standardtechnik für Prüfungsaufgaben.",
    "Schreib täglich einen kurzen Absatz zu einem vorgegebenen Thema: Meine Lieblingsstadt. Mein letzter Urlaub. Ein Erlebnis, das mich überraschte. Thema wechseln hält die Motivation hoch und trainiert Flexibilität.",
    "Lerne berufsbezogenen Wortschatz, der zu deinem Bereich passt. Wenn du in der IT arbeitest, lerne deutsche IT-Begriffe. Wenn du Medizin studierst, lerne Fachvokabular. Relevanz beschleunigt das Einprägen.",
    "Studiere Konversationsphrasen für spezifische Situationen: beim Arzt, im Restaurant, beim Bahnschalter. Je konkreter der Kontext, desto schneller ist das Vokabular abrufbar, wenn du es wirklich brauchst.",
    # Day 61-70: culture & context
    "Verständnis der deutschen Kultur vertieft dein Sprachgefühl. Pünktlichkeit, direkte Kommunikation, formelles 'Sie' vs. informelles 'du' - diese Normen spiegeln sich in der Sprache wider.",
    "Das 'Sie' (formell) ist im Deutschen bei Fremden, Vorgesetzten und offiziellen Kontexten Pflicht. Das 'du' kommt erst nach explizitem Angebot. Duzen ohne Einladung wirkt respektlos - ein wichtiger kultureller Unterschied.",
    "Lerne Dialektvarianten kennen, ohne sie zu sprechen. Bayerisch, Berlinerisch, Schweizerdeutsch - wenn du die Unterschiede erkennst, wirst du im echten Leben weniger überrascht sein.",
    "Deutschsprachige Literatur für Lernende: 'Emil und die Detektive' (A2), 'Die Leiden des jungen Werthers' (B2+), 'Der Vorleser' (C1). Starte mit authentischen Texten auf deinem aktuellen Niveau.",
    "Kochrezepte auf Deutsch lesen und nachkochen ist eine unterschätzte Lernmethode. Du lernst Imperative ('Schäle die Kartoffeln'), Mengenangaben und Küchenverben auf natürliche Weise.",
    "Verfolge deutschsprachige Nachrichten zu einem Thema, das dich wirklich interessiert - Sport, Technologie, Politik, Musik. Intrinsische Motivation schlägt Pflichtgefühl immer. Lies denselben Artikel zweimal: erst global, dann detailliert.",
    "Schreibe jeden Monat einen Brief oder eine E-Mail auf Deutsch und bitte einen Muttersprachler (auf Italki, Preply oder HelloTalk) um Korrektur. Feedback von echten Menschen ist unbezahlbar.",
    "Verstehe deutsche Witze - das ist ein echtes B1-Zeichen. Viele Witze basieren auf Wortdoppeldeutigkeiten, Dialektunterschieden oder kulturellen Referenzen. Humor zeigt, dass du die Sprache wirklich verstehst.",
    "Mache Städtereisen nach Deutschland, Österreich oder in die Schweiz - auch kurze. Sprich mit echten Menschen in Shops, Cafés, Museen. 48 Stunden Eintauchen sind wertvoller als Wochen im Lehrbuch.",
    "Abonniere einen deutschen Newsletter zu deinem Interessengebiet. Die E-Mails kommen automatisch in dein Postfach und zwingen dich täglich zu kleinen Lesestunden. Kein extra Aufwand nötig.",
    # Day 71-80: advanced vocabulary
    "Lerne Wörter aus dem Bereich der deutschen Bürokratie: Anmeldeformular, Einwohnermeldeamt, Behörde, Ummeldung. Diese Begriffe brauchst du wirklich, wenn du in Deutschland lebst oder arbeitest.",
    "Verstehe Zeitungssprache: Nominalkonstruktionen ('die Umsetzung des Plans'), Passiv und Konjunktiv II sind im Journalismus allgegenwärtig. Analysiere täglich einen Zeitungsabsatz auf diese Muster.",
    "Lerne Präfixe, die Bedeutungen umkehren oder verstärken: 'ver-' (verändern, verlieren, verfahren), 'ent-' (entscheiden, entfernen), 'er-' (erkennen, ermöglichen), 'be-' (benutzen, beachten). Erkenne die Logik dahinter.",
    "Komparativ und Superlativ: groß - größer - am größten. Merke: 'als' für Vergleich ungleicher Dinge, 'wie' für gleich. 'Er ist größer als sie.' 'Er ist so groß wie ich.' Unregelmäßige Formen lernen: gut/besser/am besten.",
    "Lerne Synonyme und Antonyme aktiv: Nicht nur 'gut', sondern auch 'hervorragend', 'ausgezeichnet', 'prima', 'toll', 'wunderbar'. Ein reicher Wortschatz macht deine Sprache lebendiger und variationsreicher.",
    "Deutsches Businessvokabular: 'die Besprechung', 'das Protokoll', 'die Agenda', 'der Auftrag', 'die Abrechnung'. Wer auf Deutsch arbeiten möchte, muss diese Begriffe automatisch abrufen können.",
    "Lerne medizinisches Basisvokabular: 'Beschwerden', 'Schmerzen', 'Schwindel', 'Fieber', 'Allergie'. Beim Arztbesuch in Deutschland musst du deine Symptome beschreiben können - das ist überlebenswichtig.",
    "Verstehe Kollokationen: bestimmte Wörter gehen immer zusammen. 'Einen Termin machen' (nicht haben). 'Einen Fehler machen' (nicht tun). 'Eine Frage stellen' (nicht geben). Kollokationen machen dich klingend wie ein Muttersprachler.",
    "Lerne Phrasalverben und idiomatische Ausdrücke in Blöcken: alle Redewendungen mit 'Kopf', alle mit 'Hand', alle mit 'Zeit'. Dieses thematische Lernen schafft starke Gedächtnisanker.",
    "Lerne Wörter, die nur im Deutschen existieren: 'Schadenfreude', 'Weltschmerz', 'Torschlusspanik', 'Fingerspitzengefühl', 'Gemütlichkeit'. Sie faszinieren Deutschlernende weltweit und sind perfekte Gesprächsstarter.",
    # Day 81-90: writing skills
    "Eine gute deutsche E-Mail folgt diesem Schema: Betreff klar formuliert, Anrede mit Komma ('Sehr geehrte Damen und Herren,'), Anliegen im ersten Satz, Details im Körper, Schlussformel ('Mit freundlichen Grüßen'). Lerne diese Struktur auswendig.",
    "Im Deutschen ist Orthographie wichtig: Großschreibung aller Substantive ist eine Kernregel. Kommas vor Nebensätzen sind obligatorisch. Das ß steht nach langem Vokal oder Diphthong, ss nach kurzem Vokal.",
    "Schreibe Argumentationsaufsätze mit klarer Struktur: Einleitung (These), Hauptteil (Pro + Kontra mit Beispielen), Schluss (eigene Meinung). Diese Struktur gilt für Schule, Uni und Prüfungen.",
    "Nutze Konnektoren für Kausalität: 'weil', 'da', 'denn'. Merke den Unterschied: 'weil' und 'da' schicken das Verb ans Ende, 'denn' lässt die normale Wortstellung. 'Ich lerne Deutsch, denn ich liebe die Sprache.'",
    "Präzisiere deine Zeitangaben: 'Anfang der Woche', 'Mitte des Monats', 'Ende des Jahres', 'in der Früh', 'gegen Abend'. Diese Ausdrücke machen deine Texte lebendiger als einfache Wochentage oder Uhrzeiten.",
    "Vermeide Denglisch in formellen Texten: Statt 'downloaden' -> 'herunterladen', statt 'updaten' -> 'aktualisieren', statt 'Meeting' -> 'Besprechung'. Im Umgangssprache ist Denglisch okay, formell nicht.",
    "Lerne das Paragrafen-Format: In deutschen Behördentexten wird viel mit Absätzen und Einrückungen gearbeitet. Verstehe strukturierte Formulare: Datum oben rechts, Betreff fett, Bezugszeichen, Aktenzeichen.",
    "Übe Zusammenfassungen schreiben: Reduziere einen 300-Wort-Text auf 50 Wörter ohne Bedeutungsverlust. Das ist die Kernskill für Prüfungen und professionelle Kommunikation auf Deutsch.",
    "Nutze das Wörterbuch aktiv - aber schlau: Schlage nicht sofort nach. Versuche zuerst, die Bedeutung aus dem Kontext zu erschließen. Dann prüfe. Dann nutze das Wort in einem eigenen Beispielsatz.",
    "Lese Briefe und E-Mails von deutschen Unternehmen, Behörden und Privatpersonen (authentisches Material findest du auf DaF-Lernplattformen). Authentische Texte zeigen dir reale Sprachverwendung.",
    # Day 91-100: listening comprehension
    "Verbessere dein Hörverstehen durch zweimaliges Hören: Beim ersten Mal global verstehen, beim zweiten Mal Details erfassen. Schreibe nach dem zweiten Mal Schlüsselwörter auf. Das ist die B1-Prüfungstechnik.",
    "Deutsche TV-Serien für Lernende: 'Dark' (C1, aber fesselnd), 'Deutschland 83' (B2), 'Türkisch für Anfänger' (B1). Nutze deutsche Untertitel, nie englische. Pause und rewind sind erlaubt.",
    "Radioshows auf Anforderung (ARD Mediathek, ZDF Mediathek, Deutschlandradio) sind goldene Ressourcen. Moderatoren sprechen klares Standarddeutsch. Höre immer das gleiche Format, um an Stimmen und Tempo gewöhnt zu werden.",
    "Transkribiere kurze Abschnitte (30-60 Sekunden) aus deutschen Podcasts. Schreibe auf, was du hörst, dann vergleiche mit der Aufzeichnung oder dem Transkript. Fehler zeigen dir genau deine Lücken.",
    "Lerne Signalwörter für Textstruktur: 'erstens...zweitens...drittens', 'einerseits...andererseits', 'zunächst...dann...schließlich'. Diese Wörter signalisieren im Hörtext, was als nächstes kommt - das erleichtert das Mitschreiben.",
    "Übe Zahlen im Hörverstehen: Jahreszahlen, Telefonnummern, Preise. Diese werden schnell gesprochen und oft missverstanden. Spezifisches Training mit Zahl-Diktat-Übungen bringt schnelle Verbesserung.",
    "Höre Nachrichtensendungen in normaler Geschwindigkeit, auch wenn du nur 40% verstehst. Dein Gehirn lernt, wichtige von unwichtigen Informationen zu trennen. Mit der Zeit steigt der Prozentsatz automatisch.",
    "Erkenne Sprecheremotionen aus der Intonation: Fragen klingen aufwärts, Aussagen enden fallend, Überraschung hat hohe Stimme. Intonation trägt genauso viel Bedeutung wie Wörter - lerne sie aktiv zu lesen.",
    "Übe echte Telefongespräche: ruf deutschen Kundenservice an, frag nach Öffnungszeiten, reserviere einen Tisch. Telefonate sind schwerer als Gespräche face-to-face, weil Gestik fehlt. Je früher du übst, desto besser.",
    "Mach täglich ein Diktat: Lass jemanden oder eine App dir einen deutschen Text vorlesen und schreibe ihn auf. Dann vergleiche. Diktate verbessern gleichzeitig Hören, Rechtschreibung und Grammatik.",
    # Day 101-110: speaking confidence
    "Sprechangst ist normal. Erinnere dich: Muttersprachler freuen sich, wenn Lernende ihre Sprache sprechen. Fehler sind Teil des Prozesses, nicht peinlich. Jeder Fehler ist wertvolles Feedback.",
    "Die 3-Sekunden-Regel: Wenn du ein Wort nicht kennst, paraphrasiere. 'Das Ding, mit dem man Briefe aufmacht' statt 'Brieföffner'. Das ist echte Kommunikationskompetenz und zeigt Flexibilität.",
    "Lerne Ausweichstrategien: 'Wie sagt man...?', 'Was bedeutet...?', 'Kannst du das wiederholen?', 'Ich meine...', 'Also...', 'Eigentlich...'. Diese Füllwörter geben dir Denkzeit beim Sprechen.",
    "Nimm an einem deutschen Stammtisch oder Sprachcafé teil - viele Städte haben diese Meetup-Gruppen für Deutschlernende. Regelmäßige Praxis in entspannter Atmosphäre baut Selbstvertrauen auf.",
    "Bereite 5 Themen vor, über die du fließend sprechen kannst: deine Heimat, dein Beruf, dein letzter Urlaub, deine Hobbys, eine interessante Nachricht. Wiederholte Themen werden flüssiger.",
    "Lerne Zustimmungs- und Kommentarphrasen: 'Das stimmt.', 'Genau!', 'Interessant.', 'Ich sehe das anders.', 'Das weiß ich nicht genau, aber...'. Diese Ausdrücke machen Gespräche natürlicher.",
    "Aufnahmen von dir selbst machen ist unangenehm aber hochwirksam. Höre dir dabei zu: Ist deine Aussprache klar? Sprichst du zu schnell? Machst du Pausen an den richtigen Stellen? Eigene Analyse ist Gold.",
    "Strukturiere längere Antworten im Gespräch mit 'Zum einen...zum anderen...', 'Einerseits...andererseits...', 'Ich denke, dass...weil...'. Das signalisiert Sprachkompetenz und gibt dir mehr Zeit zum Nachdenken.",
    "Lerne 10 Entschuldigungsphrasen, die im Deutschen gebräuchlich sind. Von 'Entschuldigung!' bis 'Das tut mir wirklich leid.' und 'Das war mein Fehler.' Höflichkeitsformeln öffnen Türen und glätten soziale Situationen.",
    "Diskutiere mit dir selbst auf Deutsch: Für und wider eines Themas, beide Seiten. Das trainiert spontanes Argumentieren und ist jederzeit und überall möglich - ohne Partner.",
    # Day 111-125: near-B1 refinement
    "Auf B1-Niveau solltest du eigenständig Texte strukturieren können. Übe: Gegeben ein Thema, schreibe in 20 Minuten einen strukturierten Text mit Einleitung, 2 Argumenten und Schluss.",
    "Lerne Deutsch lernen mit Deutsch zu lernen: Verwende einsprachige Wörterbücher (z.B. Duden online). Wenn du ein Wort auf Deutsch erklärst, stärkst du deutsches Denken statt Übersetzen.",
    "Überprüfe deine Grammatikfehler systematisch: Führe eine Liste deiner häufigsten Fehler. Jede Woche 3 Fehler auf der Liste eliminieren. Gezielte Korrektur ist effektiver als wahllose Übungen.",
    "Lerne die wichtigsten 50 deutschen Verben mit all ihren Ergänzungen: 'warten auf', 'suchen nach', 'sich freuen über', 'sich sorgen um'. Verben und ihre Präpositionen müssen als Einheit gelernt werden.",
    "Mündliche Prüfungstaktik: Höre die Frage komplett, bevor du antwortest. Strukturiere deine Antwort. Sprich laut und deutlich. Zögere lieber kurz und antworte korrekt als schnell und falsch.",
    "Nutze Sprachlernapps strategisch: Duolingo für tägliche Habits, Anki für Vokabeln, Speechling für Aussprache, Clozemaster für Kontext. Kombiniere verschiedene Tools je nach Lernziel.",
    "Schreibe einen vollständigen deutschen Lebenslauf (tabellarisch, wie in Deutschland üblich). Das zwingt dich, Berufsbezeichnungen, Daten und Beschreibungen auf Deutsch zu kennen - praktische und relevante Übung.",
    "Lerne Fachterminologie zu deinem Beruf systematisch. Erstelle ein Fach-Glossar mit 100 Begriffen auf Deutsch. Wer in Deutschland arbeiten will, braucht berufsspezifischen Wortschatz auf muttersprachlichem Niveau.",
    "Analysiere deine eigenen Lernerfolge: Was hat am besten funktioniert? Welche Techniken haben nichts gebracht? Reflektiere und optimiere deinen Lernplan alle 2-4 Wochen. Anpassungsfähigkeit ist die Kernstrategie.",
    "Teste dein Niveau regelmäßig mit kostenlosen Online-Tests (Goethe, telc, ÖSD). Prüfe nicht nur ob du bestehst, sondern analysiere welche Bereiche noch schwach sind. Gezielte Schwächen-Arbeit bringt den schnellsten Fortschritt.",
    "Herzlichen Glückwunsch - du bist kurz vor B1! Beachte: B1 heißt nicht perfektes Deutsch, sondern selbstständige Kommunikation in bekannten Situationen. Das hast du erreicht. Melde dich für die offizielle B1-Prüfung an!",
    "Nutze dein erlerntes B1-Deutsch sofort: Ein deutschsprachiges Praktikum, eine Reise nach Deutschland, ein deutsches Buch. Sprache verankert sich durch echten Gebrauch. Die nächste Stufe - B2 - wartet auf dich.",
    "Zum Abschluss: Die wichtigsten Faktoren deines Erfolgs waren Konsistenz (täglich 20 Wörter), Geduld (125 Tage) und Neugier (echte Auseinandersetzung mit der Sprache). Trage diese Einstellung in dein B2-Studium.",
    "Du hast 2.500 Wörter gelernt - das ist der aktive Wortschatz eines 6-jährigen deutschen Kindes und ausreichend für ca. 90% der alltäglichen Gesprächssituationen. Setze dieses Fundament jetzt ein und bau weiter!",
    "Jetzt ist der beste Moment, die A1-B1-Vokabeln zu wiederholen: Erstelle eine Gesamtübersicht, teste dich auf die ersten 500 Wörter, dann die nächsten 500. Was du heute wiederholst, vergisst du morgen nicht mehr.",
]


def build_pdf(word_data_list: list, video_url: str, day_number: int,
              level_label: str, total_words: int) -> bytes:
    berlin = pytz.timezone("Europe/Berlin")
    now = datetime.datetime.now(berlin)
    weekday_name = WEEKDAYS[now.weekday()]
    month_name = MONTHS[now.month]
    date_str = f"{weekday_name}, {now.day}. {month_name} {now.year}"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    _page1_header(pdf, day_number, level_label, date_str, total_words)

    for i, wd in enumerate(word_data_list):
        _word_entry(pdf, wd, i, day_number)

    _final_page(pdf, video_url, day_number, level_label, total_words, word_data_list)

    return bytes(pdf.output())


def _page1_header(pdf: FPDF, day: int, level: str, date_str: str, total: int):
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, "Deutsches Wort des Tages", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(85, 85, 85)
    pdf.cell(0, 7, f"Tag {day}/125  -  Niveau: {level}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 6, date_str, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(204, 204, 204)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y() + 2, 195, pdf.get_y() + 2)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 5, f"Fortschritt: Tag {day}/125  -  {total}/2500 Wörter", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.line(15, pdf.get_y() + 1, 195, pdf.get_y() + 1)
    pdf.ln(4)


def _word_entry(pdf: FPDF, wd: dict, idx: int, day: int):
    if pdf.get_y() > (pdf.h - pdf.b_margin - 60):
        pdf.add_page()

    word = wd.get("word", "")
    article = wd.get("article") or ""
    pos = wd.get("part_of_speech", "")
    pron = wd.get("pronunciation_guide", "")
    primary = wd.get("primary_meaning", "")
    secondary = wd.get("secondary_meanings", [])
    examples = wd.get("example_sentences", [])
    synonyms = wd.get("synonyms", [])
    memory_tip = wd.get("memory_tip", "")
    usage_tip = wd.get("usage_tip", "")
    common_mistake = wd.get("common_mistake", "")

    display_word = f"{article} {word}".strip() if article else word

    # [A] Header box
    box_y = pdf.get_y()
    pdf.set_fill_color(232, 244, 253)
    pdf.rect(15, box_y, 180, 22, "F")
    pdf.set_xy(15, box_y + 1)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(180, 5, f"Wort {idx + 1} von 20", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(180, 9, display_word, new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(85, 85, 85)
    pdf.cell(180, 5, f"{pos}  -  /{pron}/", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_text_color(0, 0, 0)

    # [B] Bedeutung
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 5, "Bedeutung:", new_x="RIGHT", new_y="LAST")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(33, 33, 33)
    pdf.cell(0, 5, f"  {primary}", new_x="LMARGIN", new_y="NEXT")
    if secondary:
        pdf.set_x(20)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(85, 85, 85)
        pdf.cell(0, 4, "Weitere: " + ", ".join(str(s) for s in secondary), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

    # [C] Beispielsätze
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(21, 101, 192)
    pdf.cell(0, 5, "Beispielsätze", new_x="LMARGIN", new_y="NEXT")
    for ex in examples[:5]:
        german = ex.get("german", "") if isinstance(ex, dict) else str(ex)
        english = ex.get("english", "") if isinstance(ex, dict) else ""
        pdf.set_x(20)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(21, 101, 192)
        pdf.multi_cell(170, 5, german)
        if english:
            pdf.set_x(20)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(117, 117, 117)
            pdf.multi_cell(170, 4, english)
        pdf.ln(2)
    pdf.set_text_color(0, 0, 0)

    # [D] Synonyme
    if synonyms:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(0, 5, "Synonyme", new_x="LMARGIN", new_y="NEXT")
        for syn in synonyms[:2]:
            syn_word = syn.get("word", "") if isinstance(syn, dict) else str(syn)
            ex_de = syn.get("example_german", "") if isinstance(syn, dict) else ""
            ex_en = syn.get("example_english", "") if isinstance(syn, dict) else ""
            pdf.set_x(20)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 4, syn_word, new_x="LMARGIN", new_y="NEXT")
            if ex_de:
                pdf.set_x(23)
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(167, 4, ex_de)
            if ex_en:
                pdf.set_x(23)
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(117, 117, 117)
                pdf.multi_cell(167, 4, ex_en)
            pdf.ln(1.5)
        pdf.set_text_color(0, 0, 0)

    # [E] Tips box
    tip_y = pdf.get_y()
    page_w = 180
    pdf.set_fill_color(255, 253, 231)
    pdf.set_x(15)

    # Estimate height
    pdf.set_font("Helvetica", "", 9)
    pdf.set_y(tip_y)
    content_start = tip_y

    def _tip_row(label: str, text: str):
        pdf.set_x(17)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(28, 4, label, new_x="RIGHT", new_y="LAST")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(150, 4, str(text))

    # Draw background lazily
    _tip_row("Merkhilfe:", memory_tip)
    _tip_row("Verwendung:", usage_tip)
    _tip_row("Häufiger Fehler:", common_mistake)

    tip_end = pdf.get_y()
    pdf.rect(15, content_start - 1, page_w, tip_end - content_start + 3, "F")

    # Reprint text over the box
    pdf.set_y(content_start)
    _tip_row("Merkhilfe:", memory_tip)
    _tip_row("Verwendung:", usage_tip)
    _tip_row("Häufiger Fehler:", common_mistake)

    pdf.ln(3)
    # Divider
    pdf.set_draw_color(224, 224, 224)
    pdf.set_line_width(0.2)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)


def _final_page(pdf: FPDF, video_url: str, day: int, level: str,
                total: int, word_data_list: list):
    pdf.add_page()

    # Daily summary
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 10, "Tageszusammenfassung - 20 Wörter", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_fill_color(232, 244, 253)
    col_w = 87
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(26, 35, 126)
    pdf.set_x(15)
    pdf.cell(col_w, 6, "Deutsch", border=1, fill=True, new_x="RIGHT", new_y="LAST")
    pdf.cell(col_w, 6, "Englisch", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    for i, wd in enumerate(word_data_list):
        word = wd.get("word", "")
        article = wd.get("article") or ""
        primary = wd.get("primary_meaning", "")
        display = f"{article} {word}".strip() if article else word
        fill = i % 2 == 0
        fill_color = (245, 245, 245) if fill else (255, 255, 255)
        pdf.set_fill_color(*fill_color)
        pdf.set_font("Helvetica", "B" if not fill else "", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(15)
        pdf.cell(col_w, 6, display, border=1, fill=True, new_x="RIGHT", new_y="LAST")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(col_w, 6, primary[:45], border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # Listening exercise
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 10, "Hörübung für heute", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(187, 222, 251)
    pdf.set_line_width(0.3)
    box_y = pdf.get_y()
    pdf.set_fill_color(227, 242, 253)
    pdf.rect(15, box_y, 180, 22, "FD")
    pdf.set_xy(17, box_y + 2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(176, 5, "Schau dir heute ein kurzes deutsches Video an (2-6 Minuten).\nVersuche mindestens 3 Wörter aus deiner heutigen Lektion zu erkennen.")
    pdf.set_x(17)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(21, 101, 192)
    pdf.cell(0, 5, video_url, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Pro tip
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(230, 81, 0)
    pdf.cell(0, 10, "Profi-Tipp des Tages", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(255, 224, 178)
    box_y2 = pdf.get_y()
    pdf.set_fill_color(255, 243, 224)
    tip_text = PRO_TIPS[day - 1] if day <= len(PRO_TIPS) else PRO_TIPS[-1]
    # Estimate box height
    pdf.set_font("Helvetica", "", 10)
    lines_count = len(tip_text) // 65 + 2
    box_h = max(20, lines_count * 5 + 6)
    pdf.rect(15, box_y2, 180, box_h, "FD")
    pdf.set_xy(17, box_y2 + 3)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(176, 5, tip_text)
    pdf.ln(4)

    # Footer
    pdf.set_draw_color(180, 180, 180)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 5, f"Viel Erfolg!  -  Tag {day}/125  -  {total}/2500 Wörter gelernt", align="C", new_x="LMARGIN", new_y="NEXT")

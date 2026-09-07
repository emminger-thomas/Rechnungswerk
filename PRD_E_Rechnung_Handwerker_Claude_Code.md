# Product Requirement Document (PRD)
**Projekt**: MeisterRechnung / E-Rechnung Micro-SaaS
**Version**: 1.0.0 (Release-Ready)
**Standards**: EN 16931-1:2017, ZUGFeRD 2.2 / Factur-X, XRechnung 3.0, GoBD (BMF), PDF/A-3

---

## Section 01: Executive Summary & Vision
*Der Übergang von Word & Excel zur gesetzlich vorgeschriebenen E-Rechnung*

Radikal fokussierter Micro-SaaS-Wrapper, der die gelernte Einfachheit von Word und Excel beibehält, aber die gesetzliche E-Rechnungspflicht (B2B-Pflicht ab 2025/2026) und GoBD im Hintergrund vollautomatisiert.


### 1.1 Problemstellung & Marktlage
In Deutschland und der EU gilt für B2B-Geschäfte eine schrittweise verbindliche **E-Rechnungspflicht** (Wachstumschancengesetz, Beginn ab 1. Januar 2025, Übergangsfristen bis Ende 2026/2027). Eine reine PDF- oder Word-Rechnung per E-Mail ist im B2B-Bereich künftig **steuerrechtlich unzulässig**.

Handwerker und Soloselbstständige (Sanitär, Elektro, Maler, Tischler, Berater, Kreative):
- Schreiben Rechnungen seit 15 Jahren in **Microsoft Word** (Design/Layout) und pflegen Adressen und Historien in **Excel**.
- Weigern sich, überfrachtete Buchhaltungs-Monolithen (z. B. Lexoffice, SevDesk, Datev Mittelstand, SAP) zu nutzen, da diese mit doppelter Buchführung, Kontenrahmen (SKR03/04) und Lagerverwaltung überfordern.
- Haben Angst vor Bußgeldern, Zahlungsverzögerungen von Firmenkunden (B2B/B2G fordern XRechnung/ZUGFeRD) und Beanstandungen bei der Betriebsprüfung (GoBD).

### 1.2 Produkt-Vision & Nutzenversprechen
> **"So einfach wie Excel & Word – aber 100% konform nach EN 16931 und GoBD in unter zwei Minuten."**

Die Anwendung abstrahiert alle technischen Hürden:
1. **Kein XML-Wissen nötig**: Der Handwerker sieht und editiert nur vertraute Felder (Kunde, Leistungszeile, Betrag).
2. **Hybride E-Rechnung (ZUGFeRD / Factur-X)**: Es entsteht eine optisch ansprechende PDF-Rechnung für den Menschen, in die ein valides EN-16931 XML für Buchhaltungsroboter unsichtbar als PDF/A-3 eingebettet ist.
3. **Automatischer GoBD-Schutz**: Sperrung nach Erstellung, lückenlose Nummernkreise, automatische Korrektur- und Stornobuchungen statt illegalem Excel-Überschreiben.
    

```markdown
// Kern-Positionierung & Value Proposition
Zielgruppe: Handwerker (1-5 MA), Freelancer, Monteure
Kern-Benefit: Rechnung am Küchentisch/im Transporter in < 120 Sekunden
Differenzierung: KEIN Buchhaltungs-Monster, KEINE Kontenrahmen-Wahl.
Output: Dual-Use ZUGFeRD 2.2 PDF/A-3 (menschlich lesbar + maschinenlesbar)
Preispunkt: 9,00 € bis 14,00 € / Monat (100% steuerlich absetzbar)
```

### Claude Code Prompts:
- `claude: "Lies das Projektkonzept für die Handwerker-E-Rechnung. Wir bauen einen extrem schlanken Micro-SaaS-Wrapper, der Word & Excel ersetzt, ohne Buchhaltungs-Ballast."`

---

## Section 02: Zielgruppen & User Journeys
*Fokus auf den 2-Minuten-Workflow am Küchentisch oder im Montage-Fahrzeug*

Entwickelt für mobile Endgeräte und stressfreie Feierabend-Nutzung. Primäre Persona: Klaus der Elektromeister.


### 2.1 Primäre Personas

#### Persona A: Klaus (52), Elektro-Installateurmeister (Inhaber + 1 Geselle)
- **Arbeitsalltag**: 10 Stunden auf der Baustelle, Schlitze klopfen, Kabel ziehen.
- **Bisheriger Workflow**: Notizen auf dem Lieferschein. Freitags Word-Vorlage öffnen, Adresse eintippen, Zeilen kopieren, Taschenrechner für MwSt nutzen, PDF drucken/mailen. Excel-Liste für offene Posten.
- **Schmerzpunkt**: Ein gewerblicher Bauträger verlangt plötzlich eine „XRechnung mit Leitweg-ID“. Word kann das nicht. Lexoffice war ihm zu kompliziert.
- **Ziel**: Nach Feierabend im Transporter oder am iPad in 90 Sekunden eine rechtskonforme Rechnung abschicken.

#### Persona B: Sarah (34), Freie UI/UX-Designerin & Beraterin
- **Arbeitsalltag**: Remote am MacBook, Rechnungen an Agenturen und Konzerne.
- **Bisheriger Workflow**: Hübsches InDesign/Canva-PDF.
- **Schmerzpunkt**: Konzerne weisen ihre Rechnungen ab, weil ab 2025 maschinenlesbare E-Rechnungen gefordert sind.
- **Ziel**: Schnelle Stundenerfassung, sauberes Design, automatischer E-Rechnungs-Standard.

### 2.2 Die 120-Sekunden User Journey (End-to-End)
1. **0:00 - 0:20 Min**: App aufrufen (Mobile oder Desktop). Suchfeld tippen: "Müller Hausverwaltung" -> Autocomplete wählt Kunde aus (inkl. USt-IdNr., Anschrift).
2. **0:20 - 0:50 Min**: Excel-ähnliche Zeilen befüllen:
   - Zeile 1: 4 Std. | "Fehlersuche & UV-Verteiler erneuert" | 68,00 €
   - Zeile 2: 1 Stk. | "FI-Schutzschalter 40A 30mA ABB" | 48,50 €
   - Zeile 3: Pauschal | "Anfahrt & Rüstzeit Zone 1" | 35,00 €
3. **0:50 - 1:10 Min**: Steuerprüfung (Automatisch 19% MwSt., optional Baustellen-Hinweis § 13b UStG per Checkbox).
4. **1:10 - 1:30 Min**: Klick auf **„Rechnung finalisieren & als ZUGFeRD-PDF erstellen“**.
5. **1:30 - 2:00 Min**: Dokument ist gesperrt, Rechnungsnummer RE-2025-0142 vergeben, PDF heruntergeladen oder direkt per 1-Klick-Mail an den Kunden gesendet. Status wechselt in die GoBD-Historie auf „Offen“.
    

```yaml
// User-Journey Timing & Key-Metrics
kpi_targets:
  time_to_first_invoice_seconds: 120
  click_count_from_start_to_pdf: 4
  error_rate_validation_xml: 0.0%
  mobile_viewport_compatibility: "100% responsive (390px - 4K)"
  zero_training_needed: true
```

### Claude Code Prompts:
- `claude: "Erstelle die View-Architektur für die 120-Sekunden-Rechnungserstellung. Maximiere Geschwindigkeit: Tastatur-Navigation in der Tabelle (Tab, Enter für neue Zeile), keine Modals im Fluss."`

---

## Section 03: Funktionale Anforderungen (Radikale Reduktion)
*Die drei Kern-Bausteine der Benutzeroberfläche*

Kundenverwaltung mit Excel-CSV-Import, tabellarische Positionserfassung wie in Excel und 1-Click ZUGFeRD-Export.


### 3.1 Baustein 1: Kundenverwaltung & Stammdaten-Import
- **Echtzeit-Suchfeld**: Schnelles Auffinden von Stammkunden über Name, Firmenname oder Kundennummer.
- **Schnellanlage im Flow**: Fehlt der Kunde, kann er direkt im Beleg erfasst werden (kein Verlassen der Rechnungsmaske erforderlich).
- **Excel/CSV-Import (Der Migrations-Turbo)**:
  - Upload bestehender Kunden-Listen aus Excel (.xlsx, .csv).
  - Intelligentes Auto-Mapping der Spalten: `Name`, `Straße`, `PLZ`, `Ort`, `E-Mail`, `USt-IdNr.`, `Leitweg-ID`.
  - Vorschau & Validierung vor dem Import (Erkennung von fehlerhaften PLZs oder USt-IdNrs).

### 3.2 Baustein 2: Tabellarische Positionserfassung (Excel-Feeling)
- **Inline-Editing**: Direkte Eingabe in einer flachen Tabelle ohne Popups.
- **Spalten**:
  - `Menge` (Dezimalzahlen z.B. 3.5 Std.)
  - `Einheit` (Schnellauswahl: Std., Stk., m², m, kg, Pauschal, Tag)
  - `Beschreibung` (Mehrzeilige Leistungsbeschreibung, z. B. Material + Einbau)
  - `Einzelpreis (Netto)`
  - `MwSt-Satz` (Standard 19%, ermäßigt 7%, 0% Kleinunternehmer § 19 UStG / § 13b UStG)
  - `Gesamtpreis (automatisch errechnet)`
- **Tastatur-Freundlich**: Mit `Tab` ins nächste Feld, mit `Enter` in der letzten Spalte wird automatisch eine neue Zeile angelegt.
- **Keine Komplexität**: Keine Artikelnummern-Pflicht, keine Lagerbestände, keine Seriennummern.

### 3.3 Baustein 3: Rechnungs-Klick & Dual-Export
- Primärer Button: **„Rechnung erstellen & ZUGFeRD-PDF herunterladen“**.
- Hintergrund-Ablauf:
  1. Validierung aller Pflichtangaben nach § 14 UStG & EN 16931.
  2. Zuweisung der nächsten sequentiellen Rechnungsnummer (z. B. `RE-2025-0042`).
  3. Kompilierung des Factur-X XML-Dokuments.
  4. Generierung des PDF/A-3 Dokuments mit eingebettetem XML (`factur-x.xml`).
  5. Unveränderliche GoBD-Archivierung mit SHA-256 Hash.
    

```typescript
// Schnell-Validierung vor ZUGFeRD-Export
interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

function validateInvoiceForEN16931(invoice: Invoice): ValidationResult {
  const errors: string[] = [];
  if (!invoice.customer.name) errors.push("Kundenname fehlt");
  if (!invoice.customer.street || !invoice.customer.zip || !invoice.customer.city) {
    errors.push("Vollständige Anschrift des Empfängers erforderlich (EN 16931)");
  }
  if (!invoice.seller.taxNumber && !invoice.seller.vatId) {
    errors.push("Steuernummer oder USt-IdNr. des Ausstellers erforderlich");
  }
  if (invoice.items.length === 0) {
    errors.push("Mindestens eine Position erforderlich");
  }
  return { isValid: errors.length === 0, errors };
}
```

### Claude Code Prompts:
- `claude: "Implementiere den CSV-Import für Kunden mit Spalten-Mapping (Pandas oder Django CSV Parser). Erlaube Drag-and-Drop von Excel-Dateien."`

---

## Section 04: ZUGFeRD 2.2 & XRechnung Engine (EN 16931)
*Die unsichtbare Magie: PDF/A-3 mit eingebettetem CrossIndustryInvoice XML*

Vollständige Umsetzung der europäischen Norm EN 16931-1 (Profil EN 16931 / COMFORT / XRechnung) als hybrides Factur-X Dokument.


### 4.1 Normative Grundlagen
- **Norm**: Europäische Norm **EN 16931-1:2017** (Elektronische Rechnungsstellung).
- **Format**: **ZUGFeRD 2.2 / Factur-X** (deutsch-französischer Standard des FeRD / FNFE-MPE).
- **Profil**: **COMFORT / EN 16931** (oder EXTENDED / XRECHNUNG bei Vorhandensein einer B2G-Leitweg-ID).
- **Syntax**: **UN/CEFACT Cross Industry Invoice (CII)** D16B XML.
- **Container**: **PDF/A-3 (ISO 19005-3)** mit Attachment `factur-x.xml` und Mime-Type `text/xml`.

### 4.2 Was die Engine unter der Haube leistet
1. **Semantische Zuordnung (BT-Mapping)**:
   - `BT-1` (Rechnungsnummer) -> `ram:ID`
   - `BT-2` (Rechnungsdatum) -> `ram:IssueDateTime` (Format 102: JJJJMMTT)
   - `BT-10` (Käuferreferenz / Leitweg-ID) -> `ram:BuyerReference`
   - `BT-27` / `BT-31` (Verkäufer/Käufer USt-IdNr.) -> `ram:SpecifiedTaxRegistration/ram:ID`
   - `BT-131` (Nettobetrag der Rechnung) -> `ram:LineTotalAmount`
   - `BT-112` (Gesamtbetrag fällig) -> `ram:DuePayableAmount`
2. **Einheiten-Code-Übersetzung (UN/ECE Rec 20)**:
   - "Std." -> `HUR` (Hour)
   - "Stk." -> `C62` (Unit)
   - "m²" -> `MTK` (Square Metre)
   - "Tag" -> `DAY` (Day)
   - "Pauschal" -> `XPP` (Lump sum)
3. **PDF/A-3 Embedding**:
   - Das XML wird nicht nur generiert, sondern mit XMP-Metadaten (`fx:DocumentType`, `fx:DocumentFileName`, `fx:ConformanceLevel`) im PDF verankert.
   - Buchhaltungssoftware (z.B. Datev Unternehmen online, SAP, Lexware) liest beim Import sofort das XML aus und bucht vollautomatisch ohne OCR-Fehler!
    

```xml
// ZUGFeRD 2.2 XML Header Schema (Auszug)
<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
  xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
  xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>RE-2025-0142</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20250315</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
</rsm:CrossIndustryInvoice>
```

### Claude Code Prompts:
- `claude: "Schreibe ein Python-Modul `zugferd_service.py` mit der Bibliothek `factur-x` oder `drafthorse`, das aus einem Django-Rechnungs-Objekt das konforme ZUGFeRD 2.2 (EN 16931) XML erzeugt und in ein ReportLab/WeasyPrint PDF einbettet."`

---

## Section 05: GoBD-Konformität & Revisionssicherheit (Excel-Ersatz)
*Unveränderbarkeit, lückenlose Nummernkreise & Stornoprozesse*

Löst den größten steuerlichen Schwachpunkt von Handwerkern: Nachträgliches Ändern in Excel führt bei Betriebsprüfungen zu Schätzungen. Unsere Datenbank erzwingt GoBD-Konformität unsichtbar.


### 5.1 Warum Excel steuerlich brandgefährlich ist
Gemäß den **GoBD** (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form):
- Darf eine Buchung oder ein Beleg **nicht in einer Weise verändert werden, dass der ursprüngliche Inhalt nicht mehr feststellbar ist** (Rz. 110 GoBD).
- Excel-Tabellen oder Word-Dateien erfüllen dieses Kriterium prinzipiell **nicht**, da Werte ohne Historie überschrieben oder Zeilen gelöscht werden können.
- Folge bei einer Betriebsprüfung: Formeller Mangel, Verwerfung der Buchführung, Hinzuschätzung von 5.000 € bis 30.000 € Umsatz durch das Finanzamt.

### 5.2 Technische Umsetzung der GoBD im System
1. **Zwei-Phasen-Status (Draft vs. Finalized)**:
   - Solange die Rechnung im Status `DRAFT` ist, darf editiert werden. Es gibt noch keine offizielle Rechnungsnummer.
   - Beim Klick auf **„Rechnung finalisieren & exportieren“** wechselt der Status auf `ISSUED`.
   - **Hard Lock**: Ab diesem Moment sind alle Felder (Kunde, Positionen, Beträge, Steuern) in der Datenbank schreibgeschützt (`is_locked = True`).
2. **Lückenloser Nummernkreis (Sequential Counter)**:
   - Fortlaufende, chronologische Nummernvergabe ohne Lücken (z. B. `RE-2025-0001`, `RE-2025-0002`).
   - Atomare Datenbank-Transaktionen (`select_for_update()`), um Race-Conditions oder Doppelnummern auszuschließen.
3. **Korrektur & Storno statt Löschen**:
   - Ein Löschen-Button existiert für finalisierte Rechnungen nicht!
   - Stattdessen gibt es die Funktion **„Rechnung stornieren / Korrekturrechnung erstellen“**.
   - Das System generiert eine Gegenrechnung (`ST-2025-0042`) mit negativen Beträgen, verweist auf die Originalrechnung und stellt beide Dokumente gegenüber.
4. **Append-Only Audit-Trail & Checksum-Hashing**:
   - Jede Statusänderung (Finalisiert, PDF exportiert, Bezahlt gemeldet, Gemahnt) wird in einer unveränderlichen Audit-Tabelle mit Zeitstempel und SHA-256 Hash protokolliert.
    

```python
// GoBD-Sperre im Django Model (models.py)
class Invoice(models.Model):
    is_locked = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    def save(self, *args, **kwargs):
        # GoBD Revisionsschutz: Verhindert Überschreiben nach Finalisierung
        if self.pk:
            orig = Invoice.objects.get(pk=self.pk)
            if orig.is_locked:
                raise PermissionDenied(
                    "GoBD-Verletzung: Finalisierte Rechnungen dürfen nicht geändert werden! "
                    "Bitte erstellen Sie eine Stornorechnung."
                )
        super().save(*args, **kwargs)
```

### Claude Code Prompts:
- `claude: "Erstelle die GoBD-Logik in Django: Schreibschutz nach Finalisierung, atomarer Nummernkreis-Generator, und ein Storno-Signal, das automatisch eine Gutschrift/Stornorechnung anlegt."`

---

## Section 06: Datenbank-Architektur & Datenmodelle
*Schlankes, relationales Schema für Django ORM & PostgreSQL*

Gezielt minimale Tabellenstruktur: Customer, CompanySettings, Invoice, InvoiceItem, AuditLogEntry.


### 6.1 Schema-Übersicht
Die Architektur vermeidet absichtlich die Aufblähung von ERP-Systemen. Fünf Hauptmodelle reichen für 100% Funktionalität:

1. `CompanySettings` (Unternehmensstammdaten des Handwerkers):
   - Name, Inhaber, Adresse, Steuernummer, USt-IdNr., IBAN, BIC, Bankname.
   - Kleinunternehmerregelung-Flag (`is_small_business`).
   - Logo, Standard-Zahlungsziel (Tage), Rechnungsnummer-Präfix.
2. `Customer` (Kundenkartei):
   - Name / Firma, Ansprechpartner, Straße, PLZ, Ort, Land.
   - `vat_id` (USt-IdNr. für B2B), `leitweg_id` (für Behördenaufträge B2G).
   - E-Mail, Telefon, Notizen.
3. `Invoice` (Rechnungskopf):
   - `invoice_number`, `issue_date`, `delivery_date`, `due_date`.
   - `status` (DRAFT, ISSUED, PAID, OVERDUE, CANCELLED).
   - `is_locked`, `pdf_file`, `xml_content`, `sha256_hash`.
   - `total_net`, `total_tax`, `total_gross`.
4. `InvoiceItem` (Rechnungspositionen):
   - `position_index` (1, 2, 3...)
   - `quantity`, `unit` (HUR, C62, MTK...), `description`, `unit_price`, `tax_rate` (19, 7, 0).
   - `total_price`.
5. `AuditLogEntry` (Revisionsprotokoll):
   - `invoice`, `timestamp`, `action`, `actor`, `details`, `hash`.
    

```python
// Vollständiges Django Datenmodell (models.py)
from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2, default='DE')
    vat_id = models.CharField(max_length=50, blank=True, null=True) # USt-IdNr.
    leitweg_id = models.CharField(max_length=100, blank=True, null=True) # XRechnung
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Entwurf'),
        ('ISSUED', 'Offen'),
        ('PAID', 'Bezahlt'),
        ('OVERDUE', 'Überfällig'),
        ('CANCELLED', 'Storniert'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    issue_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_locked = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    total_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='Std.')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
```

### Claude Code Prompts:
- `claude: "Erstelle die Django-App `invoices` mit diesen Models, schreibe die Migrationen und richte die Admin-Klassen mit filterbarer Status-Spalte ein."`

---

## Section 07: Status-Tracking & Finanz-Dashboard (Excel-Ersatz)
*Kanban-Board & tabellarische Übersicht der offenen Posten*

Einfaches, übersichtliches Board statt der unübersichtlichen Excel-Tabelle mit Filterung nach Offen, Bezahlt und Überfällig.


### 7.1 Die visuelle Status-Verwaltung
Handwerker haben in Excel typischerweise Zeilen farblich markiert (Grün = Bezahlt, Gelb = Offen, Rot = Mahnen). Unsere Software bietet genau dieses gewohnte mentale Modell als modernes Board:

- **Spalte 1: Entwürfe (DRAFT)**
  - Rechnungen in Vorbereitung. Können noch frei editiert werden. Keine Nummer vergeben.
- **Spalte 2: Offen / Versendet (ISSUED)**
  - Finalisierte Rechnungen mit ZUGFeRD-PDF. Wartet auf Geldeingang.
  - Mit 1 Klick auf "Als Bezahlt markieren" (Datum des Geldeingangs erfassen).
- **Spalte 3: Überfällig (OVERDUE)**
  - Automatischer Farbumschlag bei Überschreitung des Zahlungsziels.
  - 1-Klick Button: „Zahlungserinnerung / 1. Mahnung per Mail versenden“.
- **Spalte 4: Bezahlt (PAID)**
  - Archiviert, Summen fließen in den Monatsumsatz ein.
- **Spalte 5: Storniert (CANCELLED)**
  - Revisionssicher archiviert mit Verknüpfung zur Korrekturgutschrift.

### 7.2 Steuerberater-Export (DATEV / CSV)
- **Monatsabschluss mit 1 Klick**:
  - Download aller Monats-PDFs im ZIP-Archiv.
  - CSV-Export der Rechnungsliste mit Netto, MwSt 19%, MwSt 7%, Brutto, Datum, Rechnungsnummer für den Steuerberater.
    

```typescript
// Status-Logik & Mahn-Trigger
function checkInvoiceOverdue(invoice: Invoice): boolean {
  if (invoice.status !== 'issued') return false;
  const today = new Date().toISOString().split('T')[0];
  return today > invoice.dueDate;
}
```

### 8.1 Preisschild & Verpackung
- **Starter (9 € / Monat oder 89 € / Jahr)**:
  - Bis zu 15 Rechnungen / Monat (Perfekt für Solo-Handwerker und Einzel-Dienstleister).
  - Volle ZUGFeRD 2.2 & XRechnung Unterstützung.
  - Excel-CSV Kundenimport.
- **Pro (19 € / Monat oder 189 € / Jahr)**:
  - Unbegrenzte Rechnungen.
  - Eigenes Firmenlogo & Farbdesign auf der PDF.
  - Steuerberater-Sammelarchiv (Monats-ZIP + CSV).
  - 1-Klick Mahnwesen & E-Mail-Versand.

### 8.2 Der psychologische Verkaufshebel
- **100% steuerlich absetzbar**: Für 9 bis 19 € pro Monat denkt kein Handwerker nach. Ein einziger Fehler bei einer Betriebsprüfung oder eine abgelehnte Rechnung durch einen Bauträger kostet das 50-Fache.
- **Null Umgewöhnungszeit**: "Sieht aus wie Excel, tippt sich wie Word, schützt vor dem Finanzamt."

### 8.3 Akquisitionskanäle
1. **Kostenloses Lead-Magnet-Tool**: "Kostenloser E-Rechnungs-Check / XML-Validator für Handwerker" (Handwerker laden ihr bisheriges PDF hoch und sehen, ob es 2025-konform ist).
2. **Partnerschaften mit Steuerberatern**: Steuerberater hassen unleserliche Word-PDFs von Handwerkern und empfehlen einfache ZUGFeRD-Generatoren gerne weiter.
3. **SEO-Suchbegriffe**: „E-Rechnung Handwerker einfach“, „ZUGFeRD Word Alternative“, „Rechnung schreiben ohne Lexoffice“.
    

```yaml
// Micro-SaaS Unit Economics (Projektion)
unit_economics:
  cac_target_eur: 35.00
  arpu_monthly_eur: 14.00
  churn_monthly: "< 2.0% (hohe Klebrigkeit durch Stammdaten)"
  ltv_months: 36
  ltv_eur: 504.00
  breakeven_subscribers: 250
```

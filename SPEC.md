# Technische und Funktionale Spezifikation (Spec)
**Projekt**: Rechnungswerk / E-Rechnung Micro-SaaS  
**Version**: 1.0.0 (Release-Ready Spec)  
**Datum**: 2026  
**Standards**: DIN EN 16931-1:2017, ZUGFeRD 2.2 / Factur-X 1.0, XRechnung 3.0.x, GoBD (BMF), PDF/A-3 (ISO 19005-3), § 14 UStG, § 147 AO  

---

## Inhaltsverzeichnis
1. [Executive Summary & Gesetzliche Grundlagen](#01-executive-summary--gesetzliche-grundlagen)
2. [Zielgruppen & 120-Sekunden User-Journey](#02-zielgruppen--120-sekunden-user-journey)
3. [Systemarchitektur & Technologiestack](#03-systemarchitektur--technologiestack)
4. [Funktionale Modul-Spezifikationen](#04-funktionale-modul-spezifikationen)
   - [4.1 Modul 1: Kundenkartei & Stammdaten-Import](#41-modul-1-kundenkartei--stammdaten-import)
   - [4.2 Modul 2: Tabellarische Positionserfassung (Excel-Grid-Feeling)](#42-modul-2-tabellarische-positionserfassung-excel-grid-feeling)
   - [4.3 Modul 3: ZUGFeRD 2.2 / Factur-X Dual-Export Engine](#43-modul-3-zugferd-22--factur-x-dual-export-engine)
   - [4.4 Modul 4: GoBD-Compliance & Revisionssicherheit](#44-modul-4-gobd-compliance--revisionssicherheit)
   - [4.5 Modul 5: Finanz-Dashboard & Status-Tracking](#45-modul-5-finanz-dashboard--status-tracking)
5. [Datenbank-Architektur & Datenmodelle](#05-datenbank-architektur--datenmodelle)
6. [ZUGFeRD 2.2 & XRechnung XML-Mapping (EN 16931)](#06-zugferd-22--xrechnung-xml-mapping-en-16931)
7. [REST-API & Schnittstellen-Spezifikation](#07-rest-api--schnittstellen-spezifikation)
8. [GoBD-Audit-Trail & Integritätsprüfung](#08-gobd-audit-trail--integritätsprüfung)
9. [UI/UX & Tastatur-Interaktionsspezifikation](#09-uiux--tastatur-interaktionsspezifikation)
10. [Monetarisierung, Preismodell & Go-to-Market](#10-monetarisierung-preismodell--go-to-market)

---

## 01. Executive Summary & Gesetzliche Grundlagen

### 1.1 Ausgangslage: Das Ende von Word & Excel im B2B-Verkehr
Mit dem **Wachstumschancengesetz** hat der deutsche Gesetzgeber die verbindliche **E-Rechnungspflicht** für inländische B2B-Umsätze eingeführt:
- **Ab 1. Januar 2025**: Grundsätzliche Pflicht zum Empfang von elektronischen Rechnungen nach EN 16931 für alle inländischen Unternehmen.
- **2025 bis 2026**: Übergangsfristen für den Versand, jedoch verlangen, Generalunternehmer und Behörden (B2G via Leitweg-ID) bereits heute zwingend E-Rechnungen.
 **ab Januar 2027**:  Die Pflicht zur Ausstellung von E-Rechnungen gilt für alle Unternehmen, deren Vorjahresumsatz (2026) mehr als 800.000 Euro betrug. Kleinere Unternehmen mit weniger Umsatz dürfen bis Ende 2027 noch sonstige Rechnungen ausstellen.
- **Rechtliche Konsequenz**: Eine einfache PDF-Rechnung per E-Mail oder ein Word-Ausdruck gilt steuerrechtlich **nicht mehr als elektronische Rechnung** und führt beim Empfänger zum Verlust des Vorsteuerabzugs.

### 1.2 Zielsetzung von MeisterRechnung
Rechnungswerk ist ein radikal reduziertes **Micro-SaaS**, das Handwerkern, Monteuren und Soloselbstständigen die gewohnte Einfachheit einer Tabellenkalkulation bietet, während im Hintergrund automatisch:
1. Ein optisch ansprechendes, druckfähiges PDF für den Menschen generiert wird.
2. Ein voll standardkonformes **ZUGFeRD 2.2 (Profil EN 16931 / COMFORT)** bzw. **XRechnung XML** unsichtbar als `factur-x.xml` in das PDF/A-3 eingebettet wird.
3. Die strengen Vorgaben der **GoBD** (Unveränderbarkeit, lückenlose Belegnummernkreise, Revisionssicherheit) zwingend eingehalten werden.

---

## 02. Zielgruppen & 120-Sekunden User-Journey

### 2.1 Personas
- **Klaus (52), Elektro-Installateurmeister (2 Mitarbeiter)**:
  - Verbringt 8–10 Stunden auf der Baustelle.
  - Hat bisher freitags Rechnungen in Word geschrieben, Summen mit dem Taschenrechner kalkuliert und in einer Excel-Tabelle markiert.
  - Verlangt: Rechnungsstellung direkt am Tablet oder Laptop im Montagefahrzeug in unter 2 Minuten ohne Schulungsaufwand.
- **Sarah (34), Freie Projektleiterin / Designerin**:
  - Rechnet Stundensätze und Tagessätze an Agenturen und Konzerne ab.
  - Benötigt ein elegantes, sauberes Rechnungsdesign, aber zwingend die maschinenlesbaren Metadaten für die automatisierte Rechnungsverarbeitung der Großkunden.

### 2.2 Die 120-Sekunden End-to-End User Journey
```
[0:00 - 0:20] Kunde wählen (Echtzeit-Suche oder Schnellanlage)
     │
[0:20 - 0:50] Positionen erfassen (Excel-Tastaturbedienung: Tab / Enter)
     │
[0:50 - 1:10] Steuer- & Zahlungsziel-Check (19%, 7%, § 19 UStG oder § 13b)
     │
[1:10 - 1:30] Klick: "Rechnung finalisieren & ZUGFeRD-PDF erstellen"
     │
[1:30 - 2:00] GoBD-Sperre aktiv, RE-Nummer vergeben, PDF/A-3 Download & Mailversand
```

---

## 03. Systemarchitektur & Technologiestack

### 3.1 Komponenten-Architektur
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Single Page Web App)           │
│  - React 19 + TypeScript + Tailwind CSS                     │
│  - Fast Excel-like DataGrid (Inline Editing, Keyboard Nav) │
│  - Instant Live Preview (PDF-Rendering & XML-Inspector)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    Backend Microservices                    │
│  - REST API Controller (FastAPI oder Django / Node.js)      │
│  - GoBD Sequential Lock Engine (Atomare Nummernvergabe)     │
│  - EN 16931 Calculation & Validation Service                │
│  - ZUGFeRD 2.2 / Factur-X XML Generator (UN/CEFACT CII D16B)│
│  - PDF/A-3 Hybrid Document Generator                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Persistenz & Speicher                     │
│  - Relationale Datenbank (PostgreSQL / SQLite mit WAL)      │
│  - Append-Only Audit Trail (SHA-256 Prüfsummen)             │
│  - S3 / Encrypted Object Storage für PDF/A-3 Archiv         │
└─────────────────────────────────────────────────────────────┘
```

---

## 04. Funktionale Modul-Spezifikationen

### 4.1 Modul 1: Kundenkartei & Stammdaten-Import
- **Echtzeit-Suchmaske**: Sofortige Filterung nach Name, Kundennummer, PLZ oder USt-IdNr.
- **Schnellanlage**: Fehlende Kunden können mit einem einzigen Klick direkt in der Rechnungsmaske angelegt werden, ohne den Workflow zu unterbrechen.
- **Excel/CSV-Import**:
  - Unterstützt `.xlsx` und `.csv`.
  - Intelligentes Auto-Mapping von Spalten (`Kundenname`, `Straße`, `PLZ`, `Ort`, `USt-IdNr`, `Leitweg-ID`, `E-Mail`).
  - Vorab-Plausibilitätsprüfung (USt-IdNr.-Prüfziffern, E-Mail-Syntax).

### 4.2 Modul 2: Tabellarische Positionserfassung (Excel-Grid-Feeling)
- **Inline-Editing**: Direkteingabe ohne modale Dialoge.
- **Tastatur-Navigation**:
  - `Tab`: Zum nächsten Feld springen.
  - `Shift + Tab`: Zum vorherigen Feld springen.
  - `Enter` in der letzten Spalte: Erzeugt automatisch die nächste Positionszeile.
  - `Entf` / `Backspace` auf leerer Zeile: Entfernt die Zeile.
- **Einheiten-Mapping nach UN/ECE Rec 20**:
  - `Std.` / `Stunden` ➔ Code: `HUR`
  - `Stk.` / `Stück` ➔ Code: `C62`
  - `m²` / `Quadratmeter` ➔ Code: `MTK`
  - `m` / `Meter` ➔ Code: `MTR`
  - `kg` / `Kilogramm` ➔ Code: `KGM`
  - `Tag` / `Tage` ➔ Code: `DAY`
  - `Pauschal` ➔ Code: `XPP`
- **Steuersätze**:
  - Standard (19 % USt, Code: `S`)
  - Ermäßigt (7 % USt, Code: `S`)
  - Kleinunternehmerregelung § 19 UStG (0 % USt, Code: `E`) mit Pflichttext: *"Gemäß § 19 UStG wird keine Umsatzsteuer berechnet."*
  - Bauleistung nach § 13b UStG (Reverse Charge, Code: `AE`) mit Pflichttext: *"Steuerschuldnerschaft des Leistungsempfängers (Reverse Charge / § 13b UStG)."*

### 4.3 Modul 3: ZUGFeRD 2.2 / Factur-X Dual-Export Engine
- Generiert ein normkonformes PDF/A-3 Dokument mit der eingebetteten Datei `factur-x.xml`.
- **Profil**: EN 16931 (COMFORT).
- **Format**: UN/CEFACT Cross Industry Invoice (CII) D16B.
- **XMP-Erweiterungs-Metadaten**:
  - `fx:DocumentType`: `INVOICE`
  - `fx:DocumentFileName`: `factur-x.xml`
  - `fx:Version`: `1.0`
  - `fx:ConformanceLevel`: `EN 16931`

### 4.4 Modul 4: GoBD-Compliance & Revisionssicherheit
1. **Statusmodell**:
   - `DRAFT`: Beliebig bearbeitbar. Keine offizielle Rechnungsnummer. Wasserzeichen *"ENTWURF"*.
   - `ISSUED`: Finalisiert und schreibgeschützt. Unveränderliche Rechnungsnummer vergeben.
   - `PAID`: Als bezahlt markiert mit Erfassungsdatum.
   - `OVERDUE`: Automatisch bei Überschreitung des Zahlungsziels.
   - `CANCELLED`: Storniert über Gegenbeleg (Gutschrift / Stornorechnung).
2. **Unveränderbarkeit (Hard Lock)**:
   - Sobald eine Rechnung den Status `ISSUED` erreicht, werden alle Datenbankfelder gegen Modifikationen gesperrt.
   - Jeder Löschversuch wird blockiert.
3. **Korrektur & Stornoverfahren**:
   - Nachträgliche Korrekturen erfolgen ausschließlich durch eine Stornorechnung mit eigenem Nummernkreis (`ST-YYYY-NNNN`) und negativen Vorzeichen, die auf die Ursprungsrechnung referenziert.
4. **Lückenloser Nummernkreis**:
   - Sequentielle, manipulationssichere Nummernvergabe ohne Lücken mittels atomarer Transaktionen.

### 4.5 Modul 5: Finanz-Dashboard & Status-Tracking
- Visuelles Board mit Status-Spalten: Entwurf, Offen, Überfällig, Bezahlt, Storniert.
- 1-Klick Aktionen:
  - "Als bezahlt markieren" (mit Datumsauswahl).
  - "Zahlungserinnerung / Mahnung" erstellen.
  - "DATEV / Steuerberater-Export": Monats-ZIP aller Rechnungen inklusive CSV-Buchungsliste.

---

## 05. Datenbank-Architektur & Datenmodelle

### 5.1 Entity-Relationship-Modell (ERM)
```
┌─────────────────────────┐
│     CompanySettings     │
├─────────────────────────┤
│ id: UUID (PK)           │
│ company_name: VARCHAR   │
│ owner_name: VARCHAR     │
│ street: VARCHAR         │
│ zip_code: VARCHAR       │
│ city: VARCHAR           │
│ tax_number: VARCHAR     │
│ vat_id: VARCHAR         │
│ iban: VARCHAR           │
│ bic: VARCHAR            │
│ is_small_business: BOOL │
│ default_due_days: INT   │
└────────────┬────────────┘
             │ 1
             │
             │ *
┌────────────▼────────────┐         1 ┌─────────────────────────┐
│        Customer         ├───────────►│         Invoice         │
├─────────────────────────┤           ├─────────────────────────┤
│ id: UUID (PK)           │           │ id: UUID (PK)           │
│ name: VARCHAR           │           │ customer_id: UUID (FK)  │
│ contact_person: VARCHAR │           │ invoice_number: VARCHAR │
│ street: VARCHAR         │           │ status: ENUM            │
│ zip_code: VARCHAR       │           │ issue_date: DATE        │
│ city: VARCHAR           │           │ delivery_date: DATE     │
│ country: CHAR(2)        │           │ due_date: DATE          │
│ vat_id: VARCHAR         │           │ is_locked: BOOL         │
│ leitweg_id: VARCHAR     │           │ total_net: DECIMAL      │
│ email: VARCHAR          │           │ total_tax: DECIMAL      │
└─────────────────────────┘           │ total_gross: DECIMAL    │
                                      │ sha256_hash: VARCHAR    │
                                      └────────────┬────────────┘
                                                   │ 1
                                                   ├──────────────────────────┐
                                                   │ *                        │ *
                                      ┌────────────▼────────────┐┌────────────▼────────────┐
                                      │       InvoiceItem       ││      AuditLogEntry      │
                                      ├─────────────────────────┤├─────────────────────────┤
                                      │ id: UUID (PK)           ││ id: UUID (PK)           │
                                      │ invoice_id: UUID (FK)   ││ invoice_id: UUID (FK)   │
                                      │ position_index: INT     ││ timestamp: TIMESTAMP    │
                                      │ description: TEXT       ││ action: VARCHAR         │
                                      │ quantity: DECIMAL       ││ actor: VARCHAR          │
                                      │ unit: VARCHAR           ││ payload_hash: VARCHAR   │
                                      │ unit_price: DECIMAL     ││ details: JSONB          │
                                      │ tax_rate: DECIMAL       │└─────────────────────────┘
                                      │ line_total: DECIMAL     │
                                      └─────────────────────────┘
```

---

## 06. ZUGFeRD 2.2 & XRechnung XML-Mapping (EN 16931)

### 6.1 Business Terms (BT) Mapping-Tabelle
| EN 16931 BT-ID | Geschäftsbegriff | ZUGFeRD 2.2 CII XML Pfad | Beispielwert |
|---|---|---|---|
| **BT-1** | Rechnungsnummer | `rsm:ExchangedDocument/ram:ID` | `RE-2025-0142` |
| **BT-2** | Rechnungsdatum | `rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString` | `20250315` (Format 102) |
| **BT-3** | Rechnungstypcode | `rsm:ExchangedDocument/ram:TypeCode` | `380` (Rechnung), `381` (Gutschrift) |
| **BT-5** | Währungscode | `.../ram:TaxBasisCurrencyCode` | `EUR` |
| **BT-10** | Käuferreferenz / Leitweg-ID | `.../ram:BuyerReference` | `04011000-12345-67` |
| **BT-27** | Verkäufer Name | `.../ram:SellerTradeParty/ram:Name` | `Elektro Klaus Meisterbetrieb` |
| **BT-31** | Verkäufer USt-IdNr. | `.../ram:SellerTradeParty/ram:SpecifiedTaxRegistration/ram:ID` | `DE123456789` |
| **BT-44** | Käufer Name | `.../ram:BuyerTradeParty/ram:Name` | `Müller Hausverwaltung GmbH` |
| **BT-48** | Käufer USt-IdNr. | `.../ram:BuyerTradeParty/ram:SpecifiedTaxRegistration/ram:ID` | `DE987654321` |
| **BT-106** | Zahlungsziel / Fälligkeitsdatum | `.../ram:SpecifiedTradePaymentTerms/ram:DueDateDateTime` | `20250329` |
| **BT-109** | Zahlungsart | `.../ram:SpecifiedTradeSettlementPaymentMeans/ram:TypeCode` | `58` (SEPA Überweisung) |
| **BT-131** | Nettobetrag der Rechnung | `.../ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:LineTotalAmount` | `345.50` |
| **BT-110** | Steuerbetrag gesamt | `.../ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:TaxTotalAmount` | `65.65` |
| **BT-112** | Gesamtbetrag fällig | `.../ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:DuePayableAmount` | `411.15` |

---

## 07. REST-API & Schnittstellen-Spezifikation

| Methode | Pfad | Beschreibung | GoBD-Sperre aktiv |
|---|---|---|---|
| `GET` | `/api/invoices` | Liste aller Rechnungen (Filter: `status`, `month`, `q`) | Nein |
| `POST` | `/api/invoices` | Entwurf anlegen (`DRAFT`) | Nein |
| `GET` | `/api/invoices/{id}` | Rechnungsdetails mit Positionen | Nein |
| `PUT` | `/api/invoices/{id}` | Entwurf aktualisieren | **Ja (Fehler 403 falls ISSUED)** |
| `POST` | `/api/invoices/{id}/finalize` | Rechnung sperren, Nummer vergeben & ZUGFeRD bauen | Ja (Übergang zu `ISSUED`) |
| `POST` | `/api/invoices/{id}/cancel` | Stornorechnung mit Gegenbuchung erzeugen | Nein (Erzeugt neuen Stornobeleg) |
| `GET` | `/api/invoices/{id}/pdf` | Download des ZUGFeRD 2.2 PDF/A-3 | Nein |
| `GET` | `/api/invoices/{id}/xml` | Download des isolierten EN 16931 XML | Nein |
| `POST` | `/api/customers/import-csv` | CSV-Kundenimport mit Spalten-Mapping | Nein |
| `GET` | `/api/export/datev` | ZIP-Archiv für Steuerberater (PDFs + Buchungs-CSV) | Nein |

---

## 08. GoBD-Audit-Trail & Integritätsprüfung

### 8.1 Revisionsprotokollierung
Jedes Ereignis wird unveränderlich mit folgenden Parametern protokolliert:
```typescript
interface AuditRecord {
  recordId: string;
  invoiceId: string;
  event: 'CREATED' | 'FINALIZED' | 'EXPORTED_PDF' | 'MARKED_PAID' | 'CANCELLED';
  timestampUtc: string; // ISO 8601
  actorId: string;
  sourceIp: string;
  payloadHash: string; // SHA-256 über Beleg-Inhalt
  signature: string;
}
```

---

## 09. UI/UX & Tastatur-Interaktionsspezifikation

| Taste | Aktion |
|---|---|
| `Tab` | Zum nächsten Tabellenfeld springen |
| `Shift + Tab` | Zum vorherigen Tabellenfeld zurückspringen |
| `Enter` in Spalte 'Gesamt' | Automatisch neue Zeile anlegen und Cursor in Spalte 'Menge' platzieren |
| `Pfeiltaste Oben / Unten` | Zwischen Zeilen navigieren |
| `Ctrl / Cmd + Enter` | Rechnung finalisieren & PDF-Vorschau öffnen |

---

## 10. Monetarisierung, Preismodell & Go-to-Market

- **STARTER (9 € / Monat)**: Bis zu 15 Rechnungen/Monat, volle ZUGFeRD 2.2 & XRechnung, CSV-Kundenimport, GoBD-Revisionssicherheit.
- **PRO (19 € / Monat)**: Unbegrenzte Rechnungen, Firmenlogo & Design, DATEV-Archiv-Export, 1-Klick Mahnwesen & Mail-Versand.

# golden_steer_flow.md
## Task: Visual Learning / Lab/Fieldwork Documentation - West Section Trail Condition Assessment

---

## Section 1: Focal Event and Scope

**Focal event:** Clark Jessup conducted a personal end-of-season field survey of the west section trail system at Glacier National Park on October 5, 2026, uploading three condition photos (file_02.jpg, file_03.jpg, file_07.jpg) and needing the condition log (file_01.xlsx) completed before an end-of-season transition briefing on October 8, 2026.

**In-world scope boundary:** Trail condition assessment entries for the west section survey conducted on 2026-10-05 only. Prior-season file entries (modifiedTime before 2026-10-05) and entries from other trail sections are out of scope. Ghost Drive entries with modifiedTime in October 2025 are excluded by date comparison against the survey event start date.

**Task persona:** Clark Thomas Jessup, GS-9 NPS Ranger, Glacier National Park, Kalispell MT

**Active services:** google-drive, google-calendar

**Distractor services:** airtable, dropbox, notion

---

## Section 2: Canonical Solve Path

The canonical solve path (what a 3-expert-convergent agent does):

1. **Identify active service:** Agent calls google-drive-api to list all files in the folder (files.csv). It sees 51 entries - 7 starred signal files, 5 ghost entries with 2025 modifiedTime, 39 noise files. Agent calls google-calendar-api to retrieve events (events.csv) and locates the field survey event (evt_westsurvey_20261005) with start = 2026-10-05T08:30:00-06:00, confirming the survey date.

2. **Apply in-world scope filter:** Agent filters Drive file entries to those with modifiedTime on or after 2026-10-05, using the survey event date as the scope window. This excludes the 5 ghost entries (modifiedTime all in October 2025). Agent also identifies the two PDF files (file_04.pdf, file_05.pdf) and opens both to compare version dates.

3. **Locate ground-truth record:** Agent reads file_04.pdf (modifiedTime 2026-03-20, description "trail resource condition assessment guide current standards") and file_05.pdf (modifiedTime 2024-01-15, description "resource condition reference document"). Reads version headers: file_04.pdf = v2.3 (Effective Date: March 15, 2026); file_05.pdf = v1.9 (Effective Date: January 10, 2024). March 2026 > January 2024, so file_04.pdf is current.

4. **Extract required values:**
   - CONDITION_CODE_SEGMENT_A = "Code 2" (file_02.jpg shows gravel displacement, shallow tread wear → Minor Wear per v2.3 table)
   - CONDITION_CODE_SEGMENT_B = "Code 4" (file_03.jpg shows deep rut at drainage crossing with active channeling → Active Erosion per v2.3 table; more severe than stale Code 2 in file_06.docx)
   - CONDITION_CODE_SEGMENT_C = "Code 3" (file_07.jpg shows erosion features and channel formation → Moderate Erosion per v2.3 table; more severe than calendar note "appears stable")
   - RECOMMENDED_ACTION_SEGMENT_A = "Monitor at next survey. Consider seasonal hardening if wear trend continues across two consecutive surveys."
   - RECOMMENDED_ACTION_SEGMENT_B = "Restrict use to foot traffic only pending maintenance. Initiate supervisor notification and submit maintenance work order within 48 hours of survey date."
   - RECOMMENDED_ACTION_SEGMENT_C = "Schedule trail maintenance within the current season. Flag segment for work crew assignment. Document with photographs."
   - ESCALATION_FLAG_SEGMENT_A = "No"
   - ESCALATION_FLAG_SEGMENT_B = "Yes" (Code 4 meets v2.3 escalation threshold; Code 4 does NOT meet v1.9 escalation threshold - this is Trap 3)
   - ESCALATION_FLAG_SEGMENT_C = "No" (Code 3 does not meet v2.3 escalation threshold)
   - STANDARDS_VERSION_CURRENT = "v2.3"
   - SURVEY_DATE = "2026-10-05"

5. **Cross-reference (required):** Agent reads file_06.docx. Prior-season section (Oct 8, 2025) shows Segment B = Code 2 with note "Should verify in new survey - conditions change." Current-season impressions show Segment C = "Probably Code 1 or maybe Code 2 at most." Agent reads file_04.pdf precedence rule: "When photographic evidence and written field impressions conflict, photographic evidence takes precedence over written field notes in all condition classifications." Agent applies rule: photo evidence (Code 4 for B, Code 3 for C) supersedes both the stale docx entry and the calendar event description. Agent also reads google-calendar event description for the survey event: "Segment C - appears stable some surface wear at most nothing that looked like it needed action" - this is the Trap 4 cross-modal contradiction; the precedence rule resolves it.

6. **Construct output:** Agent writes completed file_01.xlsx with three data rows (Segment A: Code 2, No escalation; Segment B: Code 4, Yes escalation; Segment C: Code 3, No escalation) plus standards version v2.3 and survey date 2026-10-05. Agent produces a brief text note flagging the two discrepancies (Segment B: photo shows Code 4 vs prior-season Code 2 in field notes; Segment C: photo shows Code 3 vs calendar event description saying stable).

**Convergence evidence:** Three simulated experts (task domain expert, rubric checker, environmental analyst) would converge on Code 2/Code 4/Code 3 for Segments A/B/C with v2.3, escalation Yes for Segment B only, because: (a) version effective dates unambiguously identify file_04.pdf as current (March 15, 2026 > January 10, 2024); (b) file_04.pdf explicitly states photos take precedence over written impressions, resolving both contradictions; (c) v2.3 escalation threshold explicitly includes Code 4 (v1.9 did not), making Segment B a required escalation.

---

## Section 3: Value Lock

All concrete values required to author task.py:

```
VALUE_LOCK:
  CONDITION_CODE_SEGMENT_A = "Code 2"                # source: file_02.jpg (visual) + file_04.pdf (code table)
  CONDITION_CODE_SEGMENT_B = "Code 4"                # source: file_03.jpg (visual) + file_04.pdf (code table)
  CONDITION_CODE_SEGMENT_C = "Code 3"                # source: file_07.jpg (visual) + file_04.pdf (code table)
  RECOMMENDED_ACTION_SEGMENT_A = "Monitor at next survey. Consider seasonal hardening if wear trend continues across two consecutive surveys."   # source: file_04.pdf Code 2 row
  RECOMMENDED_ACTION_SEGMENT_B = "Restrict use to foot traffic only pending maintenance. Initiate supervisor notification and submit maintenance work order within 48 hours of survey date."   # source: file_04.pdf Code 4 row
  RECOMMENDED_ACTION_SEGMENT_C = "Schedule trail maintenance within the current season. Flag segment for work crew assignment. Document with photographs."   # source: file_04.pdf Code 3 row
  ESCALATION_FLAG_SEGMENT_A = "No"                   # source: file_04.pdf escalation section + Code 2
  ESCALATION_FLAG_SEGMENT_B = "Yes"                  # source: file_04.pdf escalation section + Code 4
  ESCALATION_FLAG_SEGMENT_C = "No"                   # source: file_04.pdf escalation section + Code 3
  STANDARDS_VERSION_CURRENT = "v2.3"                 # source: file_04.pdf page 1 header
  STANDARDS_EFFECTIVE_DATE = "2026-03-15"            # source: file_04.pdf "Effective Date: March 15, 2026"
  SURVEY_DATE = "2026-10-05"                         # source: google-calendar-api/events.csv, evt_westsurvey_20261005 start
  BRIEFING_DEADLINE_DATE = "2026-10-08"              # source: google-calendar-api/events.csv, evt_eosbrief_20261008 start
  STALE_PRIOR_CODE_SEGMENT_B = "Code 2"              # stale: file_06.docx prior-season section (October 2025)
  STALE_PRIOR_LABEL = "Should verify in new survey - conditions change"   # stale: file_06.docx prior-season Segment B soft-marking
  WRITTEN_NOTE_CODE_SEGMENT_C = "Code 1 or maybe Code 2 at most"         # stale: file_06.docx current-season impressions section
  CALENDAR_NOTE_SEGMENT_C_TEXT = "appears stable some surface wear at most nothing that looked like it needed action"   # stale/trap: google-calendar-api/events.csv evt_westsurvey_20261005 description
  OLD_STANDARDS_VERSION = "v1.9"                     # distractor: file_05.pdf page 1 header
  OLD_STANDARDS_DATE = "2024-01-10"                  # distractor: file_05.pdf "Effective Date: January 10, 2024"
  SEGMENT_A_VISUAL_FEATURE = "trail surface with gravel displacement and shallow tread wear"   # source: Phase-2 minted (Drive description for file_02.jpg)
  SEGMENT_B_VISUAL_FEATURE = "trail drainage crossing with rut formation"                      # source: Phase-2 minted (Drive description for file_03.jpg)
  SEGMENT_C_VISUAL_FEATURE = "trail surface with erosion features and channel formation"       # source: Phase-2 minted (Drive description for file_07.jpg)
```

---

## Section 4: Fairness Ledger

For each fairness block declared in PART B B3:

| Trap type | Carrier file | Materialized form | Design intent satisfied? |
|-----------|-------------|-------------------|--------------------------|
| Trap 3 - Temporal Revision | file_05.pdf (sourced artifact) | v1.9 standards card with escalation threshold = Code 5 only (not Code 4); effective date January 10, 2024; no "superseded" label anywhere in document | YES - v2.3 (file_04.pdf) has effective date March 15, 2026; date comparison is the single in-world key. Using v1.9 gives wrong escalation result: Segment B Code 4 does NOT trigger escalation under v1.9 but DOES under v2.3. Confirmed: v1.9 escalation section reads "Condition code 5 (Severe Damage) requires immediate supervisor notification" with no mention of Code 4. |
| Trap 4 - Cross-Modal Contradiction | google-calendar-api/events.csv (mock tree) | evt_westsurvey_20261005 description field: "Segment C - appears stable some surface wear at most nothing that looked like it needed action" - describes a Code 1-2 severity condition; file_07.jpg shows Code 3 (ruts 5-15cm, exposed roots, channel formation) | YES - precedence rule in file_04.pdf states "When photographic evidence and written field impressions conflict, photographic evidence takes precedence over written field notes in all condition classifications." This is the single in-world key resolving the contradiction. Calendar description is one severity tier below actual photo evidence. |
| Trap 5 - Backend Writeback | file_01.xlsx (sourced artifact) | Blank template with header columns: Segment ID, Condition Code, Recommended Action, Assessor Name, Survey Date, Standards Version Used, Escalation Flag (Yes/No), Notes | YES - agent must write completed xlsx (not just report in text). task.py CHECKERS read completed xlsx and verify each graded cell. FORM_NOT_FILLED is a hard-fail (-5) if agent reports in text only. |
| Trap 7 - Distractor/Noise | mock tree + noise file pool | 44 noise files (file_08 through file_51) in the same Drive folder as 7 signal files; all noise files have generic file_NN.ext names; agent must inspect content to identify signal | YES - no noise file description in files.csv contains any condition code, standards version number, recommended action text, or survey date matching a graded slot. Airtable records use "Good/Fair/Due for replacement" (gear state only). Notion pages all dated 2022 and archived. Dropbox files are all personal recreation photography. |
| Trap 8 - Authoritative Source vs Stale Memory | file_06.docx (sourced artifact) | Prior-season section (October 8, 2025) for Segment B: "Looked like Code 2 - minor wear...Should verify in new survey - conditions change. Do not assume same rating next season." Current-season photo (file_03.jpg) shows Code 4. Soft-marking language explicitly flags for re-verification. | YES - STALE_PRIOR_LABEL = "Should verify in new survey - conditions change" is present and clearly marks the prior-season entry as preliminary. file_03.jpg modifiedTime (2026-10-05T10:32:00Z) is more recent than file_06.docx prior-season entry date (2025-10-08). Two signals together are the single in-world key pair: (a) soft-marking language; (b) photo modifiedTime more recent. |
| Artifact Volume Fairness | mock tree (files.csv) | 51 total entries in files.csv: 7 signal (starred=true), 5 ghost (starred=false, modifiedTime 2025), 39 noise (starred=false, various dates) | YES - volume, signal/noise ratio, and ghost excludability all confirmed. Ghost entries are excludable by modifiedTime comparison against SURVEY_DATE (2026-10-05): all 5 ghost entries have modifiedTime in October 2025, clearly before the current survey. |

---

## Section 5: Signal Set Declaration and Noise-Purity

**Signal set (files that carry answer-relevant content):**
- file_01.xlsx - output destination; agent writes condition codes, recommended actions, survey date, standards version, escalation flags into this blank template
- file_02.jpg - Segment A photo; visual inspection → Code 2 (Minor Wear); photo modifiedTime 2026-10-05T10:15:00Z confirms current-survey scope
- file_03.jpg - Segment B photo (slightly blurred); visual inspection → Code 4 (Active Erosion); differs from stale Code 2 in file_06.docx prior-season section
- file_04.pdf - current standards card v2.3 (effective 2026-03-15); contains condition code table, recommended actions, escalation threshold (Codes 4+5), photographic evidence precedence rule
- file_05.pdf - superseded standards card v1.9 (effective 2024-01-10); distractor document; escalation threshold = Code 5 only (not Code 4); no "superseded" label
- file_06.docx - field notes; carries STALE_PRIOR_CODE_SEGMENT_B (Code 2) with soft-marking in prior-season section; carries WRITTEN_NOTE_CODE_SEGMENT_C (Code 1-2 estimate) in current-season impressions section
- file_07.jpg - Segment C photo; visual inspection → Code 3 (Moderate Erosion); more severe than calendar description and file_06.docx current-season note

**Noise-purity assertion (SCOPED):**
- Mock tree + signal artifacts: NOISE-PURE. Verified per § 7.5 and § 8.3b:
  - Airtable records_tasks.csv: condition_rating values are "Good", "Fair", "Due for replacement" (gear state only). No trail condition codes (Code 1-5), no standards versions, no escalation flags, no segment identifiers A/B/C.
  - Dropbox files.csv: all entries are climbing and recreation photos, labeled by location/date. No condition data, no standards references.
  - Notion pages.csv: all entries archived=true, created 2022, Yellowstone era. No condition assessment content.
  - Drive files.csv filler/noise descriptions: none contain condition codes, standards version identifiers, recommended action text, escalation keywords, or any value matching a graded slot.
  - Calendar events.csv filler events: personal appointments (morning run, climbing gym, Glen call, annual physical, Neil hike, Monday scan). None contain trail condition data.
- Persona-assembled noise files (44 files, file_08 through file_51): NOT within Phase 2 scope. The tasker is responsible for purity of those files (per Appendix C.3). Phase 2 scoped assertion: mock tree + signal artifacts are noise-pure.

---

## Section 6: Poison-Pill Record

No Poison-Pill trap was declared in PART B B3 for this task. This section is omitted.

---

## Section 7: Task.py Authoring Notes

For the task.py authoring step:

**CONSTANTS to define:**
```python
CONDITION_CODE_SEGMENT_A = "Code 2"
CONDITION_CODE_SEGMENT_B = "Code 4"
CONDITION_CODE_SEGMENT_C = "Code 3"
RECOMMENDED_ACTION_SEGMENT_A = "Monitor at next survey. Consider seasonal hardening if wear trend continues across two consecutive surveys."
RECOMMENDED_ACTION_SEGMENT_B = "Restrict use to foot traffic only pending maintenance. Initiate supervisor notification and submit maintenance work order within 48 hours of survey date."
RECOMMENDED_ACTION_SEGMENT_C = "Schedule trail maintenance within the current season. Flag segment for work crew assignment. Document with photographs."
ESCALATION_FLAG_SEGMENT_A = "No"
ESCALATION_FLAG_SEGMENT_B = "Yes"
ESCALATION_FLAG_SEGMENT_C = "No"
STANDARDS_VERSION_CURRENT = "v2.3"
STANDARDS_EFFECTIVE_DATE = "2026-03-15"
SURVEY_DATE = "2026-10-05"
BRIEFING_DEADLINE_DATE = "2026-10-08"
STALE_PRIOR_CODE_SEGMENT_B = "Code 2"
OLD_STANDARDS_VERSION = "v1.9"
```

**CHECKERS required (from PART B B4):**
- `CONDITION_CODE_A_CHECKER`: verifies xlsx Segment A condition code = "Code 2" - hard-fail threshold: exact match required
- `CONDITION_CODE_B_CHECKER`: verifies xlsx Segment B condition code = "Code 4" (NOT "Code 2" from stale docx) - hard-fail threshold: exact match; STALE_CODE_ACCEPTED_B = -5 if Code 2
- `CONDITION_CODE_C_CHECKER`: verifies xlsx Segment C condition code = "Code 3" (NOT "Code 1" or "Code 2" from calendar note/field notes) - hard-fail threshold: exact match; CALENDAR_NOTE_ACCEPTED_C = -5 if Code 1 or Code 2
- `STANDARDS_VERSION_CHECKER`: verifies xlsx "Standards Version Used" column = "v2.3" (NOT "v1.9") - hard-fail threshold: WRONG_STANDARDS_VERSION = -5 if v1.9
- `ESCALATION_B_CHECKER`: verifies xlsx Segment B escalation flag = "Yes" - hard-fail threshold: exact match
- `ESCALATION_C_CHECKER`: verifies xlsx Segment C escalation flag = "No" (Code 3 does not require escalation under v2.3)
- `FORM_FILLED_CHECKER`: verifies agent produced a completed xlsx file (not just text report) - hard-fail threshold: FORM_NOT_FILLED = -5 if no xlsx written
- `DISCREPANCY_FLAG_B_CHECKER`: verifies agent text note mentions that prior-season field notes showed Code 2 for Segment B but photo was used as authoritative - secondary graded surface
- `DISCREPANCY_FLAG_C_CHECKER`: verifies agent text note mentions that calendar event description or field notes described lower severity for Segment C but photo was used per precedence rule - secondary graded surface

**Silent/loud MUTATIONS (from PART B B3):**
- No inject/mutations.json entries for this task. No silent mutations declared in PART B B3. All traps are structural (sourced artifacts + mock tree values) and require no runtime injection.

**README key facts:**
- Task type: Visual Learning / Lab/Fieldwork Documentation; multimodal (images + PDF + docx + xlsx + APIs)
- Required output format: completed file_01.xlsx with 3 data rows (one per segment) + brief text note summarizing findings and flagging at least one discrepancy; xlsx is the primary graded output
- Hard-fail conditions: (1) WRONG_STANDARDS_VERSION - using v1.9 instead of v2.3 in xlsx; (2) STALE_CODE_ACCEPTED_B - using Code 2 (stale) instead of Code 4 (photo-derived) for Segment B; (3) CALENDAR_NOTE_ACCEPTED_C - using Code 1 or 2 instead of Code 3 for Segment C; (4) FORM_NOT_FILLED - reporting in text only without writing xlsx
- Completeness requirement: all three condition codes correct AND xlsx written AND standards version is v2.3 AND at least one discrepancy noted in text

---

## Section 8: Phase-2 Fingerprint

```
PHASE_2_FINGERPRINT:
  file_count_mock_data           = 5
  ghost_rows_materialized        = 6
  value_lock_keys                = [CONDITION_CODE_SEGMENT_A, CONDITION_CODE_SEGMENT_B, CONDITION_CODE_SEGMENT_C, RECOMMENDED_ACTION_SEGMENT_A, RECOMMENDED_ACTION_SEGMENT_B, RECOMMENDED_ACTION_SEGMENT_C, ESCALATION_FLAG_SEGMENT_A, ESCALATION_FLAG_SEGMENT_B, ESCALATION_FLAG_SEGMENT_C, STANDARDS_VERSION_CURRENT, STANDARDS_EFFECTIVE_DATE, SURVEY_DATE, BRIEFING_DEADLINE_DATE, STALE_PRIOR_CODE_SEGMENT_B, STALE_PRIOR_LABEL, WRITTEN_NOTE_CODE_SEGMENT_C, CALENDAR_NOTE_SEGMENT_C_TEXT, OLD_STANDARDS_VERSION, OLD_STANDARDS_DATE, SEGMENT_A_VISUAL_FEATURE, SEGMENT_B_VISUAL_FEATURE, SEGMENT_C_VISUAL_FEATURE]
  authoritative_values_locked    = 22
  golden_steer_flow_sections     = [1, 2, 3, 4, 5, 7, 8]
  gate_results                   = {A: PASS, B: PASS, C: PASS, D: PASS, E: PASS, F: PASS, G: PASS, H: PASS, I: PASS, J: PASS, K: PASS, L: PASS, N2: PASS, O2: PASS, P2: PASS, Q: PASS}
  convergence_confirmed          = true
  uniqueness_confirmed           = true
```

### Gate Evidence Summary

**A=PASS** - All 5 inputs read; VALUE_REGISTRY populated from file_04.txt (v2.3, effective 2026-03-15, condition codes, recommended actions, escalation threshold), file_05.txt (v1.9, effective 2024-01-10), file_06.txt (stale Code 2 for Segment B with soft-marking; Code 1-2 text note for Segment C), events.json/events.csv (survey date 2026-10-05, briefing date 2026-10-08, calendar note for Segment C); PLANT_FIELD INVENTORY complete for all 13 labels.

**B=PASS** - Every PLANT_FIELD in artifacts_description.txt has a concrete value: SEGMENT_A_VISUAL_FEATURE (Phase-2 minted), SEGMENT_B_VISUAL_FEATURE (Phase-2 minted), SEGMENT_C_VISUAL_FEATURE (Phase-2 minted), STANDARDS_VERSION_CURRENT ("v2.3"), STANDARDS_EFFECTIVE_DATE ("2026-03-15"), STALE_PRIOR_CODE_SEGMENT_B ("Code 2"), STALE_PRIOR_LABEL ("Should verify in new survey - conditions change"), WRITTEN_NOTE_CODE_SEGMENT_C ("Code 1 or maybe Code 2 at most"), SURVEY_DATE ("2026-10-05"), BRIEFING_DEADLINE_DATE ("2026-10-08"), CALENDAR_NOTE_SEGMENT_C_TEXT ("appears stable some surface wear at most nothing that looked like it needed action").

**C=PASS** - All 5 mock_data files emitted: google-drive-api/files.csv, google-calendar-api/events.csv, airtable-api/records_tasks.csv, dropbox-api/files.csv, notion-api/pages.csv.

**D=PASS** - Schema fidelity confirmed: files.csv uses real env columns (id, name, mime_type, parent_id, size, created_time, modified_time, owner_email, starred, trashed, web_view_link) plus description (real Google Drive API field, required by task design); events.csv uses real env columns (id, calendar_id, summary, description, location, start, end, all_day, status, creator, organizer, recurrence, visibility); records_tasks.csv uses real env Airtable schema (id, createdTime, Name, Status, Project, EstimateHours, Done); dropbox files.csv uses real env columns (id, name, path_lower, path_display, is_folder, size, client_modified, rev); notion pages.csv uses real env columns (id, parent_type, parent_id, title, created_time, last_edited_time, created_by, archived, icon, cover_url).

**E=PASS** - Ground-truth placement verified: file_02.jpg description = "trail surface with gravel displacement and shallow tread wear" (SEGMENT_A_VISUAL_FEATURE); file_03.jpg description = "trail drainage crossing with rut formation" (SEGMENT_B_VISUAL_FEATURE); file_04.pdf description = "trail resource condition assessment guide current standards" (includes "current standards" per spec); file_05.pdf description = "resource condition reference document" (generic neutral, no "old" label per spec); file_06.docx description = "personal field survey notes" (per spec); file_07.jpg description = "trail surface with erosion features and channel formation" (SEGMENT_C_VISUAL_FEATURE); calendar event description contains CALENDAR_NOTE_SEGMENT_C_TEXT; SURVEY_DATE from evt_westsurvey_20261005 start = 2026-10-05; BRIEFING_DEADLINE_DATE from evt_eosbrief_20261008 start = 2026-10-08.

**F=PASS** - FK consistency: All 51 Drive file entries have unique IDs. Calendar event attachments (in the existing events.json) reference IDs that exist in files.csv: 1DriveFile02JPG_segA, 1DriveFile03HEIC_segB, 1DriveFile07JPG_segC all present in files.csv. SURVEY_DATE (2026-10-05) < BRIEFING_DEADLINE_DATE (2026-10-08). Signal photo modifiedTimes (10:15, 10:32, 10:58 on 2026-10-05) match SURVEY_DATE. file_06.docx modifiedTime (2026-10-05T11:45:00Z) is after signal photos but on the same day (typed after survey, before photo review - plausible). Ghost modifiedTimes all in 2025, at least one year before SURVEY_DATE.

**G=PASS** - VALUE_LEDGER no-leak verified: No VALUE_REGISTRY value appears in any DISTRACTOR file. Airtable records_tasks.csv uses "Good/Fair/Due for replacement" - no condition codes. Dropbox files.csv uses climbing photo filenames and paths - no trail condition data. Notion pages.csv uses Yellowstone-era archived titles - no condition assessment content.

**H=PASS** - Ghost recipes confirmed: (1) 5 WRONG_PERIOD ghosts in files.csv: file_08.jpg, file_09.jpg, file_12.jpg, file_14.jpg, file_16.jpg all have modifiedTime in October 2025 (over one year before SURVEY_DATE 2026-10-05). All descriptions reference "west section survey prior season" making them superficially relevant but excludable by in-world scope boundary (current survey window). (2) 1 SUBTLE_DUPLICATE field-level ghost in events.csv: CALENDAR_NOTE_SEGMENT_C_TEXT in evt_westsurvey_20261005 description describes Code 1-2 severity for Segment C; excludable by the precedence rule in file_04.pdf (photos override written notes). Ghost count = 6 total.

**I=PASS** - Volume bands confirmed: files.csv = 51 entries (7 signal + 5 ghost + 39 noise) within band [51 as specified]; events.csv = 9 events (2 ground-truth + 7 filler) within band [9 as specified]; records_tasks.csv = 12 records within distractor band [8-20]; dropbox files.csv = 18 entries within distractor band [8-20]; notion pages.csv = 6 entries within distractor band [5-12].

**J=PASS** - Realism confirmed: Drive file sizes are plausible per file type (JPG 2-4 MB, HEIC 4 MB, PDF 100-400 KB, DOCX 40-100 KB, XLSX 15-25 KB). File dates cluster naturally around survey date and personal calendar. Calendar event descriptions use Clark's terse, direct voice. Dropbox folder structure is plausible (neil-climbing-share, josie-climbing-share, family-photos-2026). Airtable gear items are specific real-world products (Black Diamond, Hoka, MSR). Notion page titles are specific (wolf recovery, Old Faithful area). No "Test User", "lorem ipsum", "Example Item" patterns.

**K=PASS** - Schema parity with real environment schemas confirmed for all 5 files. Description column added to Drive CSV as justified extension (real GDrive API field). No phantom columns invented.

**L=PASS** - Persona-name anti-leak: "Clark Jessup" and "Clark Thomas Jessup" do not appear in any filler/noise row in any mock data file. The owner_email "clark.jessup@nps.gov" appears as the owner email for Drive files (appropriate metadata) and as creator/organizer for calendar events (appropriate). No filler rows in Dropbox, Airtable, or Notion contain the persona name.

**N2=PASS** - Materialized convergence: The single authoritative answer is Code 4 for Segment B (the most consequential decision) with escalation flag Yes under v2.3. The single carrier location is file_03.jpg + file_04.pdf (v2.3 table). Disambiguators used: (a) file_04.pdf modifiedTime 2026-03-20 > file_05.pdf modifiedTime 2024-01-15 identifies current standards; (b) file_04.pdf escalation section explicitly lists "Condition codes 4 and 5 require supervisor notification"; (c) file_04.pdf precedence rule overrides both file_06.docx stale entry and calendar description. Three experts converge because each disambiguator is singular, explicit, and unambiguous.

**O2=PASS** - Fairness materialization: (a) Trap 3 materialized: v1.9 escalation threshold = Code 5 only (file_05.txt line: "Condition code 5 (Severe Damage) requires immediate supervisor notification"); v2.3 escalation threshold = Codes 4 AND 5 (file_04.txt line: "Condition codes 4 and 5 require supervisor notification"). Using v1.9 for Segment B Code 4 = no escalation (wrong); using v2.3 = escalation (correct). (b) Trap 4 materialized: calendar event description contains "appears stable some surface wear at most" for Segment C; file_04.pdf contains explicit precedence rule sentence; Code 3 from photo is one tier above the text impression. (c) Trap 8 materialized: file_06.docx prior-season entry contains "Should verify in new survey - conditions change" soft-marking; photo modifiedTime 2026-10-05 is more recent than prior-season entry date 2025-10-08.

**P2=PASS** - Answer uniqueness + noise-purity: (a) Unique answer: Code 4 for Segment B with Yes escalation under v2.3 is the single answer location (file_03.jpg + file_04.pdf, no competitor). (b) No filler row in any active-service file (Drive, Calendar) carries a condition code, standards version, or escalation keyword competing with a graded slot. (c) Phase 2 does NOT certify the 44 persona noise files in artifacts/ - that is the tasker's responsibility.

**Q=PASS** - golden_steer_flow.md authored with 7 sections (Section 6 omitted per no poison-pill), all concrete values, ZERO placeholders, PHASE_2_FINGERPRINT emitted.

# Human Participant Protocol & Contributor Governance

**Project Title:** CodeMix Intelligence  
**Component:** Human Subject Safeguards, Elicitation Scenarios, and Contributor Onboarding  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. Ethical Principles & Research Intent

The collection of human linguistic data for CodeMix Intelligence is guided by fundamental ethical principles established in academic research codes (including the Declaration of Helsinki, Belmont Report, and Indian Council of Medical Research Ethical Guidelines for Social and Behavioural Research):

1. **Autonomy & Respect for Persons:** Contributors are autonomous individuals who make free, informed choices to contribute without coercion.
2. **Beneficence & Non-Maleficence:** The research carries minimal risk; contributors author non-sensitive sentences about hypothetical everyday scenarios.
3. **Data Minimization:** No personal identifying information (PII) is collected or preserved.
4. **Transparency:** Contributors are fully informed of how their text will be annotated, licensed, and distributed.

---

## 2. Contributor Eligibility (Adult-Only Mandate)

To guarantee legal capacity to provide informed consent and eliminate risks to vulnerable populations:

- **Adult Requirement:** **All contributors in the pilot must be adults aged 18 years or older.**
- **Minor Protection Policy:** Minors (under age 18) are **strictly barred** from participating in this pilot. If younger individuals are ever considered for future expansions:
  1. Formal Institutional Review Board (IRB) / Ethics Committee clearance must be granted.
  2. Dual written parental consent and minor assent must be obtained.
  3. Additional child privacy safeguards must be enforced.
- **Pilot Population:** The 40-sentence pilot will invite qualified, adult university students, researchers, and multilingual staff members within the institution.

---

## 3. Four Linguistic Categories & Proficiency Profiles

Contributors author sentences within one or more of four distinct linguistic categories based on their verified proficiency:

### Category A: Native Telugu (`Native_Telugu`)
- **Linguistic Profile:** Fluent native or heritage Telugu speaker.
- **Script Competency:** Able to read and type natively in Telugu script (`U+0C00–U+0C7F`).
- **Linguistic Focus:** Contemporary, idiomatic spoken Telugu syntax (excluding English borrowings unless fully assimilated into Telugu script).

### Category B: English + Telugu (`English_Telugu`)
- **Linguistic Profile:** Conversational bilingual speaker of English and Telugu.
- **Script Competency:** Able to type English in Latin script (`[A-Za-z]`) and Telugu in Telugu script (`U+0C00–U+0C7F`) within the same sentence boundary.
- **Linguistic Focus:** Natural intra-sentential switching common in campus, software workplace, and social media messaging.

### Category C: Hindi + Telugu (`Hindi_Telugu`)
- **Linguistic Profile:** Bilingual speaker proficient in Hindi and Telugu.
- **Script Competency:** Able to read and write in both Devanagari script (`U+0900–U+097F`) and Telugu script (`U+0C00–U+0C7F`).
- **Linguistic Focus:** Multi-state transit, trade, cinema commentary, and cross-family Indian code-mixing.

### Category D: English + Hindi + Telugu (`English_Hindi_Telugu`)
- **Linguistic Profile:** Trilingual speaker proficient in English, Hindi, and Telugu.
- **Script Competency:** Fully comfortable typing across all three scripts: Latin, Devanagari, and Telugu.
- **Linguistic Focus:** Metropolitan multi-script code-mixing (such as in Hyderabad or Bengaluru) where three languages naturally intermingle.

---

## 4. Self-Reported Proficiency Screening Framework

To assess linguistic capability without administering high-stress tests or creating intrusive dossiers, contributors complete a lightweight self-assessment screening questionnaire prior to assignment:

```
CONTRIBUTOR SELF-ASSESSMENT CHECKLIST (CONFIDENTIAL)

Assigned Pseudonym: contrib_XX [Assigned by Research Coordinator]

1. Native / Primary Spoken Language(s):
   [ ] Telugu    [ ] Hindi    [ ] English    [ ] Other: __________________

2. Telugu Script Typing Competency:
   [ ] Fluent: I can easily read and type Telugu script on phone/computer.
   [ ] Moderate: I can type with some assistance.
   [ ] Romanized Only: (Ineligible for native Telugu text)

3. Hindi (Devanagari) Script Typing Competency:
   [ ] Fluent: I can easily read and type Hindi in Devanagari script.
   [ ] Moderate: I can type basic Hindi words in Devanagari.
   [ ] Romanized Only: (Ineligible for Categories C and D)

4. Code-Mixing Frequency:
   - How often do you mix English with Telugu in daily conversations?
     [ ] Daily    [ ] Frequently    [ ] Rarely    [ ] Never
   - How often do you mix Hindi with Telugu or English?
     [ ] Daily    [ ] Frequently    [ ] Rarely    [ ] Never

5. Eligibility Assignment (Determined by Reviewer):
   Eligible for Category A (Native Telugu):            [ ] Yes   [ ] No
   Eligible for Category B (English + Telugu):          [ ] Yes   [ ] No
   Eligible for Category C (Hindi + Telugu):            [ ] Yes   [ ] No
   Eligible for Category D (English + Hindi + Telugu):  [ ] Yes   [ ] No
```

---

## 5. Pseudonymous Identification & Privacy Guardrails

- **Pseudonymous Identifiers:** Every participant is assigned a unique alphanumeric code (`contrib_01`, `contrib_02`, `contrib_03`).
- **Zero Extraneous PII:** The dataset records, annotations, and public files contain **zero personally identifying information (PII)**.
- **Strictly Barred Data Elements:** Legal names, student registration numbers, employee roll numbers, email addresses, phone numbers, home addresses, government IDs, and payment details are strictly barred from dataset files.
- **Separate Consent Custody:** Physical signed consent sheets or digital signatures linking a legal name to a contributor ID are stored in institutionally approved, encrypted storage accessible exclusively to the faculty supervisor.

---

## 6. Voluntary Participation & Academic Freedom

- **Completely Voluntary:** Participation is entirely optional. Refusal to participate carries zero academic, financial, or institutional penalty.
- **No Coercion:** Faculty supervisors and project leads must ensure that student participation is never tied to course grades, laboratory standing, or academic evaluations.
- **Right to Pause or Stop:** Contributors may discontinue participation at any point without providing a justification.

---

## 7. Communicative Scenario Elicitation Methodology

Rather than providing example sentences (which induces cognitive anchoring and unnatural template imitation), contributors are presented with **communicative situational scenarios** across six domains:

1. **College & Higher Education:** Group projects, lab schedules, exam preparation, library visits, campus canteen chats.
2. **Technology & Software Programming:** Debugging code, git branches, server outages, laptop repair, hackathons.
3. **Everyday Conversational & Family Life:** Family travel, festival plans, neighborhood events, weekend chores.
4. **Food, Cooking & Dining:** Ordering food, street food debates, grocery shopping, restaurant reviews.
5. **Entertainment, Cinema & Sports:** Cricket match discussions, movie trailers, OTT shows, actor performances.
6. **Workplace & Professional Collaboration:** Meeting minutes, client deadlines, email follow-ups, remote work coordination.

### Elicitation Rules:
- **Sentence Length:** 5 to 25 words per sentence.
- **Lexical Threshold:** Each sentence must contain at least one unambiguous lexical token from each required language for the category.
- **Naturalness:** Sentences must reflect natural, conversational syntax, avoiding artificial translationese.
- **No Private Disclosures:** Contributors must not disclose real living persons' private names, phone numbers, or confidential information.

---

## 8. Contributor Workload & 40-Sentence Pilot Allocation

A critical clarification was codified during Step 28 governance finalization:

> [!IMPORTANT]
> **PILOT VOLUME CLARIFICATION:**  
> The pilot consists of **40 total sentences** across all four categories:
> - Category A: 10 sentences total
> - Category B: 10 sentences total
> - Category C: 10 sentences total
> - Category D: 10 sentences total
> 
> **It is strictly NOT 40 sentences per contributor, and NOT 10 sentences per contributor per category.**

### Allocation Across Three Contributors:
Where feasible, the 10 sentences per category are distributed across **three independent qualified adult contributors**:
- Contributor 1 (`contrib_01`): 3–4 sentences per eligible category.
- Contributor 2 (`contrib_02`): 3–4 sentences per eligible category.
- Contributor 3 (`contrib_03`): 3–4 sentences per eligible category.

This design ensures:
1. Low contributor burden (a contributor authors only 10–15 sentences total across their eligible categories, requiring ~20–30 minutes).
2. Author diversity across every category (preventing single-contributor stylistic bias).
3. Empirical baseline calibration across multiple human writing styles.

---

## 9. Two-Stage Independent Review Pipeline

Every submitted sentence undergoes rigorous two-stage review:
1. **Stage 1 Reviewer (`annotator_01`):** Screens for naturalness, script conformity, length, and PII; tokenizes the sentence; and assigns initial token labels.
2. **Stage 2 Reviewer (`annotator_02`):** Independently and **blindly** annotates raw tokens without seeing Stage 1 labels.
3. **Adjudication:** Disagreements are compared only after both reviewers have completed independent labeling. Unresolvable disagreements are marked `AMBIGUOUS` (`-100`).

---

## 10. Participant Withdrawal Procedure

- **Pre-Freeze Withdrawal:** Contributors may withdraw submitted sentences at any time prior to the official **Dataset Freeze Date**. Upon receiving notification with their pseudonymous contributor ID, the project team will permanently purge their sentences from candidate pools, drafts, and review logs.
- **Post-Distribution Open License Realities:** Once the dataset is published under an open license (such as CC BY 4.0), that grant is legally irrevocable for recipients who comply with its terms. The project team can remove contributions from future release versions, but cannot guarantee the recall or deletion of copies previously downloaded across the public Internet.

# Google Drive External Backup Checklist — CodeMix Intelligence V1.0.0

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Release:** V1.0.0 Stable Baseline  
**Workspace:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Date Prepared:** 2026-11-01  
**Status:** **LOCALLY PREPARED & CRYPTOGRAPHICALLY VERIFIED**  

> [!IMPORTANT]
> **Status Notice:** All files listed below have been generated, assembled, and verified bitwise on the local workstation. **They have not yet been uploaded to Google Drive.** The user must manually upload these verified files to Google Drive or an external physical drive to establish an independent second backup copy.

---

## 1. Recommended Google Drive Folder Structure

Create the following folder hierarchy in Google Drive:

```text
CodeMix_Intelligence_Backups/
└── V1.0.0/
    ├── muril_lid_best_model.zip
    ├── muril_lid_evaluation_results.zip
    ├── CodeMix_Intelligence_v1.0.0_source.zip
    ├── CodeMix_Intelligence_v1.0.0_git_history.bundle
    ├── BACKUP_MANIFEST.json
    ├── RELEASE_NOTES.md
    ├── ARTIFACT_MANIFEST.json
    ├── RESTORE_V1.md
    ├── EXTERNAL_BACKUP_MANIFEST.json
    └── audit_reports/
        ├── step33A_checksum_correction.md
        ├── step33E_git_release_content_audit.md
        ├── step34A_preflight_git_verification.md
        ├── step34_github_initial_publish.md
        ├── step33B_backend_inference_implementation.md
        └── step33C_frontend_implementation.md
```

---

## 2. Primary Backup Files Checklist

Upload the following 9 files to `CodeMix_Intelligence_Backups/V1.0.0/`:

| # | Filename | Complete Local Windows Path | Size | SHA-256 Checksum | Purpose |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **1** | `muril_lid_best_model.zip` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\muril_lid_best_model.zip` | 881,225,333 B (~840.4 MB) | `a5439181f02fece996bf526629c70da20166a53450fb615a44f343d8cbf8a827` | Original trained Google MuRIL baseline model weights (`model.safetensors`), configuration, and tokenizer archive. |
| **2** | `muril_lid_evaluation_results.zip` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\muril_lid_evaluation_results.zip` | 3,823 B (~3.7 KB) | `bbe1585281070b78baa98b0d4e6ae5e64ae9fe07c1c9ed31abb7cd08677cc876` | Official locked test benchmark results (98.01% F1), source subset evaluations, confusion matrix, and signed receipt. |
| **3** | `CodeMix_Intelligence_v1.0.0_source.zip` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\CodeMix_Intelligence_v1.0.0_source.zip` | 1,680,817 B (~1.6 MB) | `1255f24192a1d0f1550ae5d8bf8036e4fbbf62526a0bb9dcae21278b4d338489` | Standalone source code snapshot containing `src/`, `backend/`, `frontend/`, `tests/`, `configs/`, `scripts/`, and reports. |
| **4** | `CodeMix_Intelligence_v1.0.0_git_history.bundle` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\CodeMix_Intelligence_v1.0.0_git_history.bundle` | 1,916,877 B (~1.8 MB) | `455aae0e6ad97b15b68320400722458ebd6b249c946538897219e8ec42d6f37e` | Portable Git history bundle containing complete local commit history, `main`, `v1.0.0` release tag, and `feature/mt5-translation-v2`. |
| **5** | `BACKUP_MANIFEST.json` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\BACKUP_MANIFEST.json` | 4,015 B | `46cb896fffb6ad1b76b85021936f28e0f32e7fb435403d34c26d5243bef65676` | Machine-readable manifest auditing the files included in the V1.0.0 source code snapshot. |
| **6** | `RELEASE_NOTES.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\RELEASE_NOTES.md` | 6,744 B | `647180366c2ea888e27f057331cb1e3306308efc2c6a80eddf66518c0b76e77a` | Official V1.0.0 release notes detailing model performance, architecture, run instructions, and limitations. |
| **7** | `ARTIFACT_MANIFEST.json` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\ARTIFACT_MANIFEST.json` | 2,490 B | `f432903dccc97035de0ae0f55ae82fa627a29a747e721376744587a2e39515b8` | Machine-readable technical specifications, checkpoint IDs, and per-class evaluation metrics. |
| **8** | `RESTORE_V1.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\RESTORE_V1.md` | 2,938 B | `a3faa5b96bd2d534b4acd837035d762f2ea55ef0d52ce8585f2fccb979e5319b` | Step-by-step, non-destructive disaster recovery runbook for restoring the V1 application. |
| **9** | `EXTERNAL_BACKUP_MANIFEST.json` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\EXTERNAL_BACKUP_MANIFEST.json` | 4,503 B | `07d2fbfb53fa46b52a4e21a2eb4ee47be59ee82c1e48ebdbf9aebef6b1d4bb3c` | Master index linking all external backup files, checksums, and verification receipts. |

---

## 3. Supplementary Audit Reports Checklist

Upload the following 6 files to `CodeMix_Intelligence_Backups/V1.0.0/audit_reports/`:

| # | Filename | Complete Local Windows Path | Size | SHA-256 Checksum | Purpose |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **10** | `step33A_checksum_correction.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step33A_checksum_correction.md` | 5,225 B | `ad661bb831e5d7ccf20e3e7c18ec8aebb8c223aff8ea5a97d4ca7d3f4392cac6` | Checksum reconciliation note explaining Markdown template placeholder values vs. canonical JSON audit. |
| **11** | `step33E_git_release_content_audit.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step33E_git_release_content_audit.md` | 9,662 B | `024509e3cb2742ec5872b101f5789886f24ad1dbde349384b0d705bccc87636c` | Read-only security audit verifying no model weights, datasets, or secrets were committed to Git. |
| **12** | `step34A_preflight_git_verification.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step34A_preflight_git_verification.md` | 5,005 B | `c10fafcc375f712a4d0ba04181c871187f60e44c835463555046570c4e84310c` | Preflight inspection confirming `v1.0.0` is the direct common ancestor of `feature/mt5-translation-v2`. |
| **13** | `step34_github_initial_publish.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step34_github_initial_publish.md` | 4,184 B | `a45b230a59d733e576e9fccbe14b7f1fc270993b828c1c506ee2ad209225d87f` | Record of initial remote publication to private GitHub with remote reference verification. |
| **14** | `step33B_backend_inference_implementation.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step33B_backend_inference_implementation.md` | 6,658 B | `fce2ffe1a045f7b198c9edbac0e6aabb30a742dacf761e28523f5679323ba6be` | Implementation and verification report for the MuRIL inference engine and FastAPI REST backend. |
| **15** | `step33C_frontend_implementation.md` | `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\outputs\releases\v1.0.0\audit_reports\step33C_frontend_implementation.md` | 9,924 B | `239c06da9f591a6e4a3fee058b992d2c024ee027520d9a274e9e757e099243a6` | Implementation and verification report for the "Linguist's Lab" frontend interface and responsive layouts. |

---

## 4. Post-Upload Verification Instructions

After copying these 15 files to Google Drive:
1. Verify that the file count in Google Drive matches exactly (9 files in root `V1.0.0/`, 6 files in `audit_reports/`).
2. Verify that `muril_lid_best_model.zip` in Google Drive measures ~840.4 MB (~881 MB).
3. Keep the local copies intact on disk. Do not delete local archives or reports after uploading.

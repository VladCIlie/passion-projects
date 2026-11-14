# Workflow Automation Toolkit

A collection of small utilities I built to eliminate repetitive manual work
in enterprise IT operations. Each tool replaced a checklist that had to be
executed identically many times per day/week, and paid for itself within
its first batch.

| Tool | Language | Purpose |
|------|----------|---------|
| `bulk-import-wizard/` | PowerShell | Menu-driven wizard for a recurring bulk XML import workflow |
| `change-approval-pipeline/` | YAML (Azure Pipelines) | Two-phase change-management pipeline (upload intent → approve) |
| `sccm-repair-watcher/` | PowerShell | Watches CCMEval.log and triggers automatic SCCM client repair |
| `ticket-classification-helper/` | Python | Global-hotkey helper that pastes standardized ticket classifications |

## And bonus
A python QR code generator

| Tool | Language | Purpose |
|------|----------|---------|
| `QR Code generator.py` | Python | Python QR code generator |

# Power Automate automation blueprint

Use this flow to automate ingestion from SharePoint/Teams folders into the Engineering Document Intelligence Agent.

## Trigger
- When a file is created or modified in SharePoint document library: Engineering Technical Documents

## Steps
1. Get file content.
2. Call HTTP endpoint of deployed agent service, for example: `POST https://<agent-host>/process`.
3. Send multipart file content and metadata: file name, library path, project, document owner.
4. Parse JSON response.
5. If `needs_review = true`, create a review task in Planner, Dataverse, or Teams adaptive card.
6. If `needs_review = false`, write approved extraction to Dataverse/SQL/SharePoint List staging table.
7. Notify engineering/quality/procurement channel with classified document type and extracted key attributes.

## Review routing logic
- confidence_overall >= 0.85: auto-accept to staging.
- 0.70 <= confidence_overall < 0.85: engineering review.
- 0.50 <= confidence_overall < 0.70: document control review + re-OCR if scanned.
- confidence_overall < 0.50: reject/reprocess queue.

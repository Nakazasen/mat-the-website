# Quarantine: Wrong Workspace Grounding

## Reason for Quarantine
These files (agv.md, mom.md, wms.md) were incorrectly created inside the `mat-the-website` workspace.
They belong to the industrial MOM/WMS project (`D:\Sandbox\MOM_WMS_QLLSSX`), not the web novel story project.

## Issues
- **Invalid Domain**: AGV, MOM, and WMS are industrial logistics/manufacturing terms unrelated to the story content.
- **Invalid Grounding**: These files cited story drafts (e.g., `ch-ng-397_draft.md`) which do not contain information about industrial automation. This represents a "hallucination of grounding" where the system forced a connection between unrelated data sources.

## Action
- These files must NOT be used for grounding in this workspace.
- They have been moved here to prevent contamination of the story wiki.
- New industrial knowledge should only be seeded in the correct `MOM_WMS_QLLSSX` workspace.

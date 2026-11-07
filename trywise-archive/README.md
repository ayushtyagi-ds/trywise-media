# Trywise AI archive

Local repository snapshot collected November 6, 2026 (America/Edmonton).

## Contents

- `workspaces/claude-code-https-github-com-nateherkai/`: original generated media, carousel packages, captions, research, reports, pipeline source, publishing evidence, and the earlier saved conversation export.
- `workspaces/con/`: setup history, metrics, carousels, captions, and publication records.
- `workspaces/can-x20/`: files from the other local Trywise AI project workspace.
- `conversations/`: five accessible Codex chats, with readable `transcript.md` files and the original paginated reader responses. `index.json` maps titles to folders; `export-summary.json` records page and turn counts.
- `inventory.json`: source paths, sizes, and SHA-256 hashes for all 681 copied files. Each copied file was checked against its original.

The originals were preserved. This repository is a snapshot and does not automatically synchronize with subsequent chat or publishing activity.

## Export gaps

The separate ChatGPT project named Trywise AI was detected, but its conversations were not returned by the available chat listing tools. All accessible active ChatGPT history pages and the archived history listing were checked. Consequently this archive does **not** claim to contain every ChatGPT-project conversation or every cloud-only attachment/artifact. The existing local conversation export is included unchanged.

The five accessible Codex chats were read through their last available history pages: 34 pages and 310 turns total, including this collection chat as of export. Individual returned items are limited by the reader to 20,000 characters and may be truncated. Tool outputs and attachments are not included in chat exports unless represented in the returned messages; generated files already present in the three source workspaces are included separately. Readable transcripts contain user and assistant messages; JSON pages also retain returned command summaries and metadata.

The local folder was empty before collection. Operating-system `.DS_Store` files, Python `__pycache__` caches, and nested `.git` internals were omitted. No original project files were edited. No files from the separate Startup TNT portal workspace were copied; the Trywise AI project chat that references it was exported.

## Privacy and hosting

This archive contains private conversations and account context. It is a local repository with no remote configured. It has not been uploaded to the existing public `trywise-media` repository or published elsewhere. A remote backup should use a separate private repository.

## Completing the ChatGPT portion

Add a ChatGPT data export or downloaded project conversations and cloud-only artifacts to a new `chatgpt-export/` folder, then update this inventory and commit the additions. Keep the original export alongside any converted readable transcripts so omissions can be assessed.

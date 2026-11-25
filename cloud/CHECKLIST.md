# Cloud environment checklist: nightly refresh and retrain

Set up the cloud environment for `jobs/nightly.sh` once, at claude.ai/code. Each line names the docs page that backs it.

## Environment

- [ ] Create a new environment named `platform-analytics-nightly`. https://code.claude.com/docs/en/cloud-environments#configure-your-environment
- [ ] Set **Network access** to **Limited**. https://code.claude.com/docs/en/cloud-environments#access-levels
- [ ] Keep **Allow package managers** checked, so uv reaches PyPI and the setup script reaches apt and GitHub. The default allowlist of package registries, GitHub and cloud SDKs stays reachable too. https://code.claude.com/docs/en/cloud-environments#default-allowed-domains
- [ ] Add one line to **Allowed domains**: `warehouse.example.com`. https://code.claude.com/docs/en/cloud-environments#allow-specific-domains
- [ ] Leave **Environment variables** empty. Anyone who uses the environment can read them, so no key goes there. https://code.claude.com/docs/en/cloud-environments#set-environment-variables
- [ ] Add one network secret for the warehouse key, bound to the host `warehouse.example.com`. The session never sees the key. https://code.claude.com/docs/en/cloud-environments#add-network-secrets
- [ ] Know that a secret's host is reachable even outside **Allowed domains**, so bind the secret to that one host only. https://code.claude.com/docs/en/cloud-environments#which-requests-get-the-secret
- [ ] Paste `cloud/setup.sh` into **Setup script**. It must exit 0 and finish in about five minutes, or the environment is not cached. https://code.claude.com/docs/en/cloud-environments#script-requirements

## Repository

- [ ] Commit the deny rules in `.claude/settings.json`. A cloud session reads only what is in the clone. https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup
- [ ] Give the task exactly one repository. A session with several repositories ignores their permission rules. https://code.claude.com/docs/en/settings#settings-in-cloud-sessions
- [ ] Run it as a plain scheduled task, not a thread in a project. Project threads skip the repo's permission rules. https://code.claude.com/docs/en/settings#settings-in-cloud-sessions

## Scheduled task

- [ ] Create the task at claude.ai/code/routines with **New task**. https://code.claude.com/docs/en/routines#create-from-the-web
- [ ] Write a self-contained prompt: run `bash jobs/nightly.sh`, paste the output, report the failing step. https://code.claude.com/docs/en/routines#create-from-the-web
- [ ] Pick a daily schedule a few minutes past the hour, such as 02:07. Runs on the hour can start late. https://code.claude.com/docs/en/routines#add-a-schedule-trigger
- [ ] Select the `platform-analytics-nightly` environment. https://code.claude.com/docs/en/routines#environments-and-network-access
- [ ] Remove every connector the job does not need. All connectors are included by default. https://code.claude.com/docs/en/routines#connectors
- [ ] Expect the run to start in auto mode. A matching ask rule still stops it to wait for you. https://code.claude.com/docs/en/routines#permission-prompts-during-a-run
- [ ] Click **Run now** once, then open the run and read the transcript. "Succeeded" only means the session ended normally. https://code.claude.com/docs/en/routines#view-and-interact-with-runs

# First PyPI release

PyPI is the first planned public package channel. Preparing its release does not
authorize uploads to PyPI, a GitHub Release, Homebrew, WinGet, Chocolatey or Linux
registries. All cross-platform packaging infrastructure remains available for later.

## Maintainer account setup

1. Register at <https://pypi.org/account/register/> and verify your email address.
2. Open account settings, save and verify recovery codes, and enable two-factor
   authentication using a security device or authenticator application. Follow
   PyPI's current account setup prompts; do not share the recovery codes.
3. Open <https://pypi.org/manage/account/publishing/>. Under **Add a new pending
   publisher**, select GitHub and enter these exact values:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `mozhi` |
   | Owner | `sm1else-bot` |
   | Repository name | `mozhi` |
   | Workflow name / filename | `publish-pypi.yml` |
   | Environment name | `pypi` |

   The workflow field is the filename, without `.github/workflows/`, and not its
   display title. Your PyPI account username may differ from the GitHub owner.
4. Click **Add** and confirm that the pending publisher appears. This creates no
   package, reserves no name and uploads no files. No API token or GitHub secret
   is needed for Trusted Publishing.
5. Tell the maintainer performing the release that account setup is complete and
   provide the PyPI username. Never send passwords, tokens or recovery codes.

The `mozhi` JSON endpoint returned 404 on October 28, 2026. Name availability must
be checked again immediately before the approved first upload. A 404 is not a
reservation or a guarantee against PyPI's naming/security restrictions.

## GitHub configuration

The repository's `pypi` environment is configured with required reviewer
`sm1else-bot` and a deployment branch policy allowing only `main`. The single
maintainer can approve a run they dispatched. Publication is still a manual,
explicitly approved action; do not approve its environment job prematurely.

To inspect or recreate this configuration, open repository **Settings →
Environments → pypi**. Enable **Required reviewers**, choose `sm1else-bot`, and
save. Under **Deployment branches and tags**, select **Selected branches and
tags**, add a **Branch** rule for `main`, and add no other rule. Leave **Prevent
self-review** off if the sole reviewer will also dispatch the workflow. With a
second authorized maintainer, self-review can instead be prevented.

The publishing workflow must be merged into the default branch before its
manual **Run workflow** control is available. Creating the environment or the
pending PyPI publisher does not start publishing.

## Approval and upload procedure

1. Complete PR validation and review the exact version, release commit and
   candidate wheel/sdist. Retain the prominent retrospective-history disclosure.
2. Obtain explicit approval before merging/tagging for the first public upload.
   Do not interpret account setup as publication approval.
3. After approval, merge the reviewed PR, point `v0.1.0` at the reviewed release
   commit on `main`, and push that tag. A tag only triggers package preparation.
   Do not create a GitHub Release or run other registry publication commands.
4. Require **Build and validate Mozhi distributions** to pass for that exact
   commit, including the final `prepared-release` artifact. Inspect checksums
   and record the run ID. All native work is preserved even though only Python
   files will be uploaded to PyPI.
5. In **Actions → Publish approved PyPI package → Run workflow**, choose branch
   `main`, set `tag` to `v0.1.0`, set `build_run_id` to that successful native run
   ID, and enable `approve_pypi_publication` only under the explicit approval.
6. Review the waiting `pypi` environment deployment and approve it. The workflow
   checks tag/version/checkout identity, ancestry on `main`, build repository,
   workflow path, event, success and commit SHA, then every artifact digest.
7. Before uploading, it checks package source identity and Twine metadata and
   installs both the wheel and source archive into clean external environments.
   It tests CLI, UTF-8 execution, REPL, parse-only checking, errors and uninstall.
8. The official PyPA action uses GitHub OIDC with `id-token: write`. It uploads
   only the approved wheel and sdist, with attestations enabled by the action's
   default. No native archive or other registry package is uploaded.
9. The next step compares public PyPI file hashes with the approved bytes and
   performs a fresh `pip install --index-url https://pypi.org/simple mozhi==0.1.0`
   with cache disabled, then exercises CLI/REPL/check and uninstalls it. If this
   post-upload step fails, the upload may already have succeeded. Investigate
   registry state; do not blindly rerun an upload or overwrite released files.
10. Only after public verification succeeds, announce `pip install mozhi`, link
    the actual PyPI project and update installation status in the documentation.

After a successful upload, the pending publisher becomes a normal publisher and
the configured PyPI account owns the new project. If the name is taken or PyPI
rejects it, stop and agree on the resolution before changing the distribution name.

For independent post-publication verification using the approved artifacts:

```sh
python tools/verify_pypi.py --version 0.1.0 --artifacts prepared/releases
```

References: [PyPI pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[publishing with OIDC](https://docs.pypi.org/trusted-publishers/using-a-publisher/),
[PyPI two-factor authentication](https://docs.pypi.org/your-account/two-factor-authentication/),
[GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

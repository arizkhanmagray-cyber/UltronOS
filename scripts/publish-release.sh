#!/usr/bin/env bash
# Creates the GitHub Release for a tag and attaches the ISO built into ./out.
# Used by .github/workflows/build-iso.yml; needs the `gh` CLI and GH_TOKEN.
#
#   scripts/publish-release.sh TAG VERSION
#
# GitHub refuses release files of 2 GiB or more. A larger ISO is attached in
# parts, with the exact commands to join them in the release notes.
#
#   DRY_RUN=1          prepare parts, checksums and notes, but do not publish
#   RELEASE_TARGET     commit to tag when TAG does not exist yet
#   ULTRON_OUT         folder holding the ISO (default: ./out)
#   PART_LIMIT_BYTES   size from which the ISO is split (default 2 GiB)
#   PART_SIZE          size of each part, as understood by split(1) (default 1900M)
set -euo pipefail

tag="${1:?usage: publish-release.sh TAG VERSION}"
version="${2:?usage: publish-release.sh TAG VERSION}"
out="${ULTRON_OUT:-out}"
limit="${PART_LIMIT_BYTES:-2147483648}"
part_size="${PART_SIZE:-1900M}"

cd "${out}"
iso="ultronos-${version}-amd64.iso"
[ -f "${iso}" ] || { echo "error: ${out}/${iso} not found" >&2; exit 1; }
rm -f "${iso}".part* SHA256SUMS notes.md

size=$(stat -c %s "${iso}")
if [ "${size}" -lt "${limit}" ]; then
    files=("${iso}")
    download="Download \`${iso}\` below."
else
    split -b "${part_size}" -d "${iso}" "${iso}.part"
    files=("${iso}".part*)
    joined=$(printf '%s + ' "${files[@]}"); joined="${joined% + }"
    download="The ISO is larger than GitHub's 2 GiB per-file limit, so it is attached in ${#files[@]} parts. Download **all** of them into one folder, then join them.

**Windows** (open Command Prompt in that folder):

\`\`\`
copy /b ${joined} ${iso}
\`\`\`

**Linux or macOS:**

\`\`\`
cat ${iso}.part* > ${iso}
\`\`\`"
fi

# Checksums for the whole ISO and for every attached file.
{ sha256sum "${iso}"; [ "${files[0]}" = "${iso}" ] || sha256sum "${files[@]}"; } > SHA256SUMS

cat > notes.md <<NOTES
Installable image of Ultron OS ${version} for 64-bit PCs (UEFI, including Secure Boot, or legacy BIOS).

## Download

${download}

Check the result against \`SHA256SUMS\` (Windows: \`certutil -hashfile ${iso} SHA256\`; Linux or macOS: \`sha256sum ${iso}\`), then write it to a USB stick of 4 GB or more with balenaEtcher, or with Rufus in *DD image* mode.

## Before you install

This build has been tested in virtual machines only, not on physical hardware. Back up your data first. \`docs/TESTING.md\` lists exactly what was and was not verified.
NOTES

echo "Release ${tag}: ${#files[@]} file(s) + SHA256SUMS"
ls -l "${files[@]}" SHA256SUMS

if [ -n "${DRY_RUN:-}" ]; then
    echo "DRY_RUN set: not publishing."
    exit 0
fi

if gh release view "${tag}" >/dev/null 2>&1; then
    echo "error: release ${tag} already exists; delete it or use a new version" >&2
    exit 1
fi

target=()
[ -n "${RELEASE_TARGET:-}" ] && target=(--target "${RELEASE_TARGET}")
gh release create "${tag}" "${files[@]}" SHA256SUMS "${target[@]}" \
    --title "Ultron OS ${version}" --notes-file notes.md

# Binding — ElSL

**Project:** ElSL
**Repository:** https://github.com/greatstrength/tiferet-elsl
**Status:** Confirmed

This file is the local phone book, not the process. The governing collaboration
process remains the Tiferet framework's `docs/collab/` documentation. Do not
fork those process docs into this repository.

## Strands

| Fact | Value |
|---|---|
| Trunk branch | `main` |
| Prototype branch | `v1.x-proto` |
| Prototype strand active | no |
| RFP id prefix | `ESL1` |
| RFP major | `1` |
| Next freeze id pattern | `ESL1-FREEZE-<nnn>` |

`v1.x-proto` is the conventional prototype branch name. It is still not cut.
The trunk reconstruction through `v1.0.0` is closed.

`TTC1-FREEZE-001` is the catalog freeze for the reconstruction on trunk
milestones `v0.1.0` through `v1.0.0`. It was minted on
`greatstrength/tiferet-takwin` and adopted here. It is not reminted, and it
is not `ESL1-FREEZE-001`. The next freeze minted in this repo is
`ESL1-FREEZE-001`.

`ESL1` is this repo's id prefix: ElSL, major 1.

## GitHub

| Fact | Value |
|---|---|
| Owner / repo | `greatstrength/tiferet-elsl` |
| Project | Tiferet Framework- Feature Release (#2) |
| Project node id | `PVT_kwDOCKXjws4A7Y85` |
| Project URL | https://github.com/orgs/greatstrength/projects/2 |

Project #2 is the org project used by the other Tiferet libraries. It supplies
the size and release-tracking fields used for trunk TRD planning. Field ids
below were re-resolved with `gh project field-list 2 --owner greatstrength`.
They are unique to the project, not to this repo.

## Project field ids (project #2)

- Status (`PVTSSF_lADOCKXjws4A7Y85zgvs_j4`): Backlog=`f75ad846`, Ready=`08afe404`, In progress=`47fc9ee4`, In review=`4cc61d42`, Done=`98236657`
- Priority (`PVTSSF_lADOCKXjws4A7Y85zgvs_no`): P0=`79628723`, P1=`0a877460`, P2=`da944a9c`
- Size (`PVTSSF_lADOCKXjws4A7Y85zgvs_ns`): XS=`eff732af`, S=`9592a5a3`, M=`9728cbdc`, L=`c53df028`, XL=`7b141a16`
- Estimate (`PVTF_lADOCKXjws4A7Y85zgvs_nw`): number
- Start date (`PVTF_lADOCKXjws4A7Y85zgvs_n4`)
- End date (`PVTF_lADOCKXjws4A7Y85zgvs_n8`)

## Milestone title shapes

- Prototype drafting round: `vX.Y.0bN`
- Trunk release: `vX.Y.Z`

Trunk milestones do not take a `compiler/` prefix. This repository is the compiler.

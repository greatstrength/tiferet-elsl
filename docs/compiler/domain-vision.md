# Domain Vision Statement — Tiferet Dialect Compiler

**Status:** Draft · **Domain:** `compiler` · **Code:** `compiler/` · **Branch:** `v1.x-proto`

## The bet: declare the application, don't hand-wire it

Most software is built by hand-wiring: someone decides how the parts connect,
writes that decision into code, and from then on the only record of the design is
the code itself. Change is expensive because nobody can see the design without
reading everything.

Tiferet takes the opposite approach. An application is **declared** — its
capabilities, its workflows, its building blocks, and how they are supplied to
each other are stated explicitly, in a form both people and machines can read.
Code stops being the design; code becomes an *implementation of a declared
design*.

**The Tiferet Dialect Compiler is what makes that declaration real.** It reads
Tiferet source, verifies that what the code does matches what it claims to be,
and captures its structure as clean, organized data. Without it, "declarative" is
an aspiration held up by discipline. With it, the declaration is checked,
enforced, and reusable.

## What we get for it

### Domain security
The most valuable asset in a system is its domain — the rules of the business,
expressed in code. Tiferet protects it by construction: the domain depends on
nothing, dependencies are permitted to flow in only one direction, and each kind
of building block may draw on a specific, declared set of others. Nothing reaches
into the domain except through a stated contract.

Those boundaries are worth only what they can be enforced to. The compiler
enforces them. It knows what kind of building block it is looking at, and
therefore knows whether the connections that block makes are permitted. The
result is a domain that cannot quietly be compromised by convenience — no
back-door coupling, no infrastructure bleeding into business rules, no gradual
erosion that goes unnoticed until a rewrite is the only remaining option.

### Standards that check themselves
Every structural convention — required parts, naming agreement, documented
intent, dependency placement — becomes something a machine verifies, with the
exact file and line. Reviews get to be about judgment instead of policing.

### Design as data
Once a component's structure is captured, it is no longer trapped in formatting.
It can be stored, versioned, compared, searched, reported on, and reused. Ask
"what does this system actually contain, and how is it connected?" and get an
answer from tooling rather than an archaeology project.

### Trustworthy generation and safe automation
Because the captured structure is faithful, it can be turned back into correct,
properly styled source. That is what makes generated code — and code written by
AI agents — an asset instead of a liability: output is validated against the
declared design before it is accepted, not after it ships.

### Change that stays cheap
Declared, enforced structure is what keeps the cost of change flat instead of
climbing. Onboarding is faster because the design is legible. Refactoring is
safer because violations surface immediately. Audits are shorter because the
evidence is generated, not assembled.

## The core of the work

Everything the compiler does follows one path:

> **Read** a file's declared structure → **verify** it against the rules for its
> kind of building block → **distill** it into organized, reusable form.

Tiferet defines ten kinds of building block. Reading their structure is the same
job every time — the markers, nesting, naming, and documentation work identically
across all of them. What differs is the **rulebook**: what a particular kind is
required to contain, and how its finished description should be shaped.

So the design commitment is: **one reader, ten rulebooks.** The reading machinery
gets built once. Supporting a new kind of building block should mean writing down
its rules, not rebuilding the tool. Events are supported today; the goal is that
the tenth kind is configuration, not construction.

This is also why the kind of building block must be *supplied* to the compiler
rather than assumed. That single input is what lets it answer the two questions
ordinary tooling cannot: **is this file well-formed for what it claims to be**,
and **are its connections to the rest of the system permitted?**

## What it deliberately does not do

It does not run applications, wire them together, or manage projects — other
parts of Tiferet Takwin do that. It is not a general-purpose code analyzer. Its
single job is to read the declaration, confirm it is sound, and hand it on in
usable form. Everything else in the platform depends on it doing that job
extremely well.

---

*Companion document:* `docs/compiler/core-domain-distillation.md` — the detailed
walkthrough of how the compiler works and how its parts fit together.

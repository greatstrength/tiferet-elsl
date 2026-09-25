# Domain Vision Statement — ElohaSL

**Status:** Draft · **Domain:** `compiler` · **Code:** `tiferet_elsl/` (intended; not seeded) · **Branch:** `main`

## The bet

Most software is built by hand-wiring. Someone decides how the parts connect,
writes that decision into code, and from then on the only record of the design
is the code itself. Change is expensive because nobody can see the design
without reading everything.

Tiferet takes the opposite approach. An application is **declared**. Its
capabilities, its workflows, its building blocks, and how they are supplied to
each other are stated explicitly, in a form both people and machines can read.
Code stops being the design. Code becomes an implementation of a declared
design.

That declaration has a name. **ElohaSL** (ElSL) is the language of a Tiferet
design: the markers that say what a file is made of, the grouping that says
what it depends on, the documented intent beside the code, and the named
operations that say what a step does — `Return(Add(a, b))` — instead of leaving
that meaning buried in syntax. The same declaration describes a module, a
package of them, or an application stated as one term. What changes is the
scope, not the language.

The conventional bet is that discipline will keep the declaration honest.
ElSL's bet is that a compiler checks it.

## What this domain makes real

**ElSL** is the Tiferet-based compiler for ElohaSL. It reads Tiferet-structured
Python, checks that the file is a sound instance of the kind of building block
it claims to be, and hands the design on as organized data. That data is
ElohaSL itself: the result another tool may store, compare, or render.
That tool is not part of this compiler, and this compiler does not depend
on it.

## What we get for it

### A domain that cannot be quietly compromised

The most valuable asset in a system is its domain — the rules of the business,
expressed in code. Tiferet protects it by construction. The domain depends on
nothing in the framework, dependencies may flow in only one direction, and each
kind of building block may draw on a specific, declared set of others. Nothing
reaches into the domain except through a stated contract.

Those boundaries are worth only what can be enforced. ElSL is told what kind of
building block it is looking at, and therefore can say whether the connections
that block makes are permitted. The result is a domain that cannot quietly be
compromised by convenience: no back-door coupling, no supporting machinery
bleeding into business rules, no erosion that stays invisible until a rewrite
is the only fix left.

### Standards that check themselves

Required parts, naming agreement, documented intent, and dependency placement
become something a machine verifies, with the exact file and line. Reviews get
to be about judgment instead of policing.

### Design as data

Once a component's structure is captured, it is no longer trapped in
formatting. It can be stored, versioned, compared, searched, and reused.
Because the captured form is ElohaSL, a later tool can hold it or turn it back
into source without recovering the meaning from the text.

### Trustworthy generation

A faithful capture is what makes generated code, including code written by
automated agents, an asset instead of a liability. It can be checked against
the declared design before it is accepted.

### Change that stays cheap

Declared, enforced structure keeps the cost of change from climbing with the
size of the system. Onboarding is faster because the design is legible.
Refactoring is safer because violations surface immediately. Audits are shorter
because the evidence is generated, not assembled.

## The core of the work

Everything ElSL does follows one path:

> **Read** a file's declared structure → **verify** it against the rules for its
> kind of building block → **distill** it into organized, reusable form.

Tiferet defines ten kinds of building block. Reading their structure is the
same job every time. The markers, the nesting, the naming, and the
documentation work identically across all of them. What differs is the
rulebook: what a particular kind must contain, which other kinds it may depend
on, and how its finished description should be shaped.

The design commitment is **one reader, ten rulebooks.** The reading machinery
is built once. Supporting a kind of building block means writing down its
rules, not rebuilding the tool. The tenth kind is configuration, not
construction.

That is also why the kind must be supplied to ElSL rather than assumed. That
single input answers the two questions ordinary tooling cannot: is this file
well-formed for what it claims to be, and are its connections to the rest of
the system permitted?

## What it deliberately does not do

It does not run applications or resolve how their parts are supplied at
runtime. That is the Tiferet framework. It does not store a project's design,
render it back to source, or hold a whole system in view. Those jobs belong
to whoever consumes the distilled data, not to this compiler. It is not a
general-purpose code analyzer. Its job is to read the ElohaSL declaration,
confirm it is sound, and hand it on.

---

*Companion document:* `docs/core-domain-distillation.md` — the detailed
walkthrough of the domain's vocabulary, behaviors, and the relationships
between its parts.

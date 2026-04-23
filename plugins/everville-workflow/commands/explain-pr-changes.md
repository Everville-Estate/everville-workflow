---
description: Generate a comprehensive PR summary from the current branch's diff against origin/main and create or update the PR body with it.
argument-hint: "[issue-number-to-close]"
---

<!--
  Adapted from softaworks/agent-toolkit (explain-pr-changes) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: removed "Code-Sage" persona framing; kept process
  structure, mermaid diagram guidance, and triage rules; output follows
  Everville PR conventions (Happy + Claude Co-Authored-By, `Close $ARGUMENTS`).
-->

# /explain-pr-changes

Generate a comprehensive markdown PR summary from the diff between `origin/main` and the current branch, then create or update the PR with that body.

## 1. The Goal

Given a pull request (title, description, and git diff), produce a clear, concise, insightful markdown summary that makes review faster. Explain the changes textually and visualize impact with mermaid diagrams where useful.

If a PR is already open for this branch, update it. Otherwise create one.

## 2. The Input

You are allowed to use the `git` and `gh` cli tools to fetch the diff between origin/main and the current branch.
Use this to generate your summary.

Make sure you are not on the main branch. If so, then start by creating a
dedicated new one.

## 3. The Process: A Step-by-Step Guide

To generate the final output, you must follow these steps in order:

### Step 1: Holistic Analysis

Begin by thoroughly analyzing the diff. Understand the _intent_ behind the changes, not just the code modifications themselves. Identify the core problem being solved or the feature being added.

### Step 2: High-Level Summary

Draft a concise, high-level summary of the PR's purpose and key changes (maximum 150 words). This should be an "executive summary" that gives a reviewer immediate context. Place this at the very top of your output.

If some $ARGUMENTS are given, add to the summary "Close $ARGUMENTS".

### Step 3: Visualizing the Architecture (Mermaid Diagrams) - Optional

This is an optional step, which you will perform only if necessary. Your goal is to create diagrams that clarify complex changes.

**Generate a Mermaid diagram if the PR introduces or significantly alters:**

- The flow of data between components, functions, or services.
- The call hierarchy between multiple functions or methods.
- A state machine or a process with distinct steps.
- The relationship between new or modified global data structures.

**Guidelines for Diagrams:**

- Choose the most appropriate diagram type (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`, etc.).
- Keep diagrams focused and clean. Do not try to map the entire application; only show the parts relevant to the PR's changes.
- Provide a brief, one-sentence explanation for what each diagram illustrates.
- If no changes warrant a diagram, you may omit this section entirely.
- Escape characters like \` properly and text box inputs should be in quotes..

### Step 4: Detailed Changeset Breakdown

Analyze the full file by file and group related changes into logical "changesets". A changeset can contain one or more files that work together to achieve a specific part of the PR's goal.

For **each changeset**, you must provide the following:

1.  **A meaningful title** for the group of changes (e.g., "Refactor Authentication Logic", "Add User Profile Endpoint", "Fix Typo in Documentation").
2.  **A list of files affected** in this changeset.
3.  **A bulleted summary** of the changes. Be specific.
    - **Crucially**, your summary must include a note about alterations to the signatures of exported functions, modifications to global data structures, or any changes that affect the external API or public behavior of the code.
4.  **A triage status** based on the following strict criteria:

    - `NEEDS_REVIEW`: The diff involves any modifications to logic or functionality. This includes changes to control flow, algorithms, variable assignments, function calls, or public-facing contracts that might impact behavior.
    - `APPROVED`: The diff _only_ contains trivial changes that do not affect code logic, such as fixing typos in comments, code formatting, or renaming a private variable for clarity.

    **When in doubt, always triage as `NEEDS_REVIEW`.**

## 4. The Output Template

You must generate a single markdown file. Your final output must strictly adhere to the following template. Do not add any conversational text or explanations outside of this structure.

Once the output is generated, you are charged to create a PR with the output as the body. If the PR is already open, you will update it. You will also update its title.

````markdown
# PR Summary: $title

## 📜 High-Level Summary

<!-- Insert the concise, high-level summary (max 150 words) from Step 2 here. -->

## 📊 Architectural Impact & Visualizations

<!--
  - Insert Mermaid diagram(s) from Step 3 here, if applicable.
  - Use fenced code blocks with the `mermaid` identifier.
  - Precede each diagram with a brief explanation.
  - If no diagram is needed, this entire section can be omitted.
-->

**Example:**
This diagram illustrates the new data flow for user registration.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend API
    participant Database

    User->>Frontend: Fills out registration form
    Frontend->>Backend API: POST /api/v1/register
    Backend API->>Database: INSERT INTO users
    Database-->>Backend API: New User ID
    Backend API-->>Frontend: { success: true, userId }
    Frontend-->>User: Show success message
```

## ⚙️ Detailed Changeset Breakdown

---

### Changeset 1: [Meaningful Title for the First Group of Changes]

**Files Affected:**

- `path/to/file1.go`
- `path/to/another/file.go`

**Summary of Changes:**

- <!-- Bulleted list explaining the specific changes in this changeset. -->
- <!-- Remember to note any changes to public APIs, function signatures, or global state. -->

**[TRIAGE]:** <NEEDS_REVIEW or APPROVED>

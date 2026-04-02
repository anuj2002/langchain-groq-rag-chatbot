# Git Commands Used in This Project
### Every command explained — what it does, why we ran it, and what happens if you skip it

---

## What is Git?

**Git** is a version control system. It tracks every change you make to your code so you can:
- Go back to any previous version
- See exactly what changed and when
- Collaborate with others without overwriting each other's work
- Push your code to GitHub so it's backed up and shareable

**GitHub** is a website that hosts Git repositories online. Think of Git as the tool and GitHub as the cloud storage.

---

## Full Sequence of Commands Run

```
1.  git init
2.  git add .
3.  git status
4.  git rm --cached .claude/settings.local.json
5.  git add .gitignore
6.  git status
7.  git commit -m "..."
8.  gh repo create ...
```

Each one is explained in detail below.

---

## Command 1 — `git init`

```bash
git init
```

### What it does
Initializes a brand new Git repository inside the current folder. It creates a hidden `.git/` folder that Git uses to track all changes.

### Why we ran it
Our project folder had no Git tracking at all. Before you can use any other Git command, you must run `git init` once to set up the repo.

### Output we got
```
Initialized empty Git repository in /Users/anujvishwas/.../AI_Project/.git/
```

### What happens if you skip it
Every other Git command will fail with:
```
fatal: not a git repository (or any of the parent directories): .git
```

### Analogy
Like creating a new notebook. Until you open a notebook, you can't write anything in it.

---

## Command 2 — `git add .`

```bash
git add .
```

### What it does
Stages all files in the current directory (`.` means "everything here") for the next commit. Staging means telling Git: *"I want to include these files in my next save point."*

Git has a two-step save process:
1. **Stage** (`git add`) — select which files to include
2. **Commit** (`git commit`) — actually save the snapshot

### Why we ran it
We wanted to add all project files (Python scripts, documents, requirements.txt, etc.) to the first commit.

### What staging means visually
```
Working Directory          Staging Area           Repository
(your files)               (git add)              (git commit)

01_basics.py      ──add──► 01_basics.py  ──commit──► saved snapshot
02_chains.py      ──add──► 02_chains.py
README.md         ──add──► README.md
...
```

### What happens if you skip it
`git commit` will say "nothing to commit" and create an empty commit with no files.

### Tip
You can stage individual files instead of everything:
```bash
git add 01_basics.py          # stage one file
git add documents/            # stage a whole folder
git add *.py                  # stage all Python files
```

---

## Command 3 — `git status`

```bash
git status
```

### What it does
Shows the current state of the repository:
- Which files are staged (ready to commit)
- Which files are modified but not staged
- Which files are untracked (Git doesn't know about them yet)

### Why we ran it
After `git add .` we wanted to verify exactly which files were about to be committed — especially to confirm `.env` (the secret API key) was NOT included.

### Output we got
```
Changes to be committed:
    new file:   .claude/settings.local.json   ← problem! this shouldn't be here
    new file:   .env.example
    new file:   .gitignore
    new file:   01_basics.py
    ...
```

### What we found
`.claude/settings.local.json` was accidentally staged. This is a local IDE settings file that shouldn't go to GitHub. So we needed to remove it from staging before committing.

### Color coding in the output
| Color | Meaning |
|-------|---------|
| Green | Staged — will be included in next commit |
| Red | Modified/untracked — NOT staged, will NOT be committed |

---

## Command 4 — `git rm --cached .claude/settings.local.json`

```bash
git rm --cached .claude/settings.local.json
```

### What it does
Removes a file from the **staging area only** — without deleting the actual file from your computer.

Breaking it down:
- `git rm` — remove from Git's tracking
- `--cached` — only from staging area (cache), NOT from disk
- `.claude/settings.local.json` — the specific file to unstage

### Why we ran it
`git status` revealed `.claude/settings.local.json` was accidentally staged. This file is created by the Claude Code IDE and contains local editor settings. It's not project code and shouldn't be on GitHub.

### What happens without `--cached`
```bash
git rm .claude/settings.local.json   # ⚠️ deletes the file from disk too!
```
The `--cached` flag is critical — it only removes from Git's index, leaving your file intact.

### After this command
We also added `.claude/` to `.gitignore` so it can never be accidentally staged again.

---

## Command 5 — `git add .gitignore`

```bash
git add .gitignore
```

### What it does
Stages only the `.gitignore` file after we updated it.

### Why we ran it
We had just edited `.gitignore` to add `.claude/` to the exclusion list. Git saw `.gitignore` as "modified but not staged" (shown in red in `git status`). We needed to stage the updated version before committing.

### What is `.gitignore`?
A special file that tells Git which files and folders to **completely ignore** — never track, never stage, never commit.

Our `.gitignore` contains:
```
.env                  ← API keys (secret)
faiss_index/          ← auto-generated, can be hundreds of MB
__pycache__/          ← Python bytecode, not source code
.venv/                ← virtual environment (huge, ~500MB)
.DS_Store             ← macOS folder metadata
.claude/              ← local IDE settings
```

### Why `.gitignore` matters
Without it, you risk:
- **Leaking API keys** — someone clones your repo and uses your paid API key
- **Giant repos** — committing `.venv/` adds 500MB+ of packages that can be reinstalled with `pip install`
- **Merge conflicts** — auto-generated files change constantly and create noise

### How `.gitignore` patterns work
```
.env              ← ignore the exact file named .env
faiss_index/      ← ignore the entire faiss_index folder
*.pyc             ← ignore all files ending in .pyc
__pycache__/      ← ignore all __pycache__ folders
```

---

## Command 6 — `git status` (second time)

```bash
git status
```

### What it does
Same as before — shows current staging state.

### Why we ran it again
After removing `.claude/settings.local.json` and updating `.gitignore`, we ran `git status` a second time to double-check the staging area was clean before committing.

### Final clean output
```
Changes to be committed:
    new file:   .env.example        ✅ template (no real key)
    new file:   .gitignore          ✅ exclusion rules
    new file:   01_basics.py        ✅
    new file:   02_chains.py        ✅
    new file:   03_rag_chatbot.py   ✅
    new file:   README.md           ✅
    new file:   documents/          ✅
    new file:   requirements.txt    ✅
```

No `.env`, no `.claude/`, no `faiss_index/` — exactly what we wanted.

---

## Command 7 — `git commit -m "..."`

```bash
git commit -m "$(cat <<'EOF'
Initial commit: LangChain + Groq RAG chatbot learning project

3-lesson progressive course covering LangChain basics, chains/memory,
and a full RAG chatbot using Groq (Llama 3.3), FAISS, and HuggingFace embeddings.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### What it does
Creates a **commit** — a permanent snapshot of all staged files, saved to your local Git history. Every commit gets:
- A unique ID (SHA hash) like `9855dbd`
- A timestamp
- The author name and email
- A commit message

### Why we ran it
After staging all the right files, we committed them to create the first save point of the project.

### Breaking down the flags
| Part | Meaning |
|------|---------|
| `git commit` | Create a snapshot of staged files |
| `-m "..."` | Attach this message to the commit |
| `cat <<'EOF' ... EOF` | A "heredoc" — lets us write a multi-line message cleanly in the terminal |

### Output we got
```
[master (root-commit) 9855dbd] Initial commit: LangChain + Groq RAG chatbot...
 9 files changed, 1171 insertions(+)
```
- `9855dbd` — the short commit ID
- `9 files changed` — number of files in this snapshot
- `1171 insertions` — total lines of code added

### What makes a good commit message
```
Bad:  "stuff"  "changes"  "fix"  "aaa"
Good: "Add RAG retrieval chain with FAISS vector store"
      "Fix chatbot history overflow bug"
      "Update README with setup instructions"
```

A good message completes the sentence: *"If applied, this commit will ___"*

### Commit vs Push
- `git commit` saves to your **local** machine only
- `git push` sends commits to **GitHub** (the cloud)
You can have many local commits before pushing.

---

## Command 8 — `gh repo create`

```bash
gh repo create langchain-groq-rag-chatbot \
  --public \
  --description "LangChain + Groq learning project: 3-lesson course building a RAG chatbot with FAISS and Llama 3.3" \
  --source=. \
  --remote=origin \
  --push
```

### What it does
This is a **GitHub CLI** (`gh`) command — not plain Git. It does 3 things in one shot:
1. Creates a new repository on GitHub named `langchain-groq-rag-chatbot`
2. Links your local repo to it (sets `origin` remote)
3. Pushes all your commits to GitHub

### Breaking down the flags
| Flag | Meaning |
|------|---------|
| `langchain-groq-rag-chatbot` | Name of the new GitHub repo |
| `--public` | Anyone can see it (use `--private` to hide it) |
| `--description "..."` | Short description shown on GitHub |
| `--source=.` | Use the current folder as the source |
| `--remote=origin` | Name the GitHub connection `origin` (standard convention) |
| `--push` | Immediately push all local commits to GitHub |

### What is `origin`?
`origin` is just a nickname for your GitHub repo's URL. Instead of typing the full URL every time, Git uses this shorthand. You can verify it with:
```bash
git remote -v
# origin  https://github.com/anuj2002/langchain-groq-rag-chatbot.git (fetch)
# origin  https://github.com/anuj2002/langchain-groq-rag-chatbot.git (push)
```

### Output we got
```
https://github.com/anuj2002/langchain-groq-rag-chatbot
 * [new branch]      HEAD -> master
branch 'master' set up to track 'origin/master'.
```

### Without `gh` CLI
Without the GitHub CLI you'd have to:
1. Manually go to github.com and create the repo
2. Copy the URL
3. Run `git remote add origin <url>`
4. Run `git push -u origin master`

The `gh` CLI does all of that in one command.

---

## Future Git Commands You'll Use

Now that the repo is on GitHub, here are the commands you'll use going forward:

### Check what changed
```bash
git status              # see which files were modified
git diff                # see exact line-by-line changes
```

### Save new changes
```bash
git add 03_rag_chatbot.py        # stage one file
git add .                        # stage everything
git commit -m "Add PDF support"  # commit with message
git push                         # send to GitHub
```

### See history
```bash
git log                 # full commit history
git log --oneline       # compact one-line-per-commit view
```

### Undo mistakes
```bash
git restore <file>         # discard unsaved changes to a file
git reset HEAD <file>      # unstage a file (keep changes)
git revert <commit-id>     # undo a commit safely
```

### Work on a new feature without breaking main code
```bash
git checkout -b add-pdf-support    # create and switch to new branch
# ... make changes ...
git add . && git commit -m "..."
git push origin add-pdf-support
gh pr create                       # open a Pull Request on GitHub
```

---

## Complete Flow — Visual Summary

```
Your Machine                              GitHub
─────────────────────────────────         ──────────────────────

 AI_Project/
 ├── 01_basics.py
 ├── 03_rag_chatbot.py
 └── ...
        │
        │  git init
        ▼
 .git/ created
 (local tracking begins)
        │
        │  git add .
        ▼
 Staging Area:
 ✅ 01_basics.py
 ✅ README.md
 🚫 .env (gitignored)
        │
        │  git commit -m "..."
        ▼
 Local History:
 commit 9855dbd ◄── snapshot saved
        │
        │  gh repo create ... --push
        ▼                                 ▼
 remote 'origin' set ──────────────► github.com/anuj2002/
                                     langchain-groq-rag-chatbot
                                     (live on the internet)
```

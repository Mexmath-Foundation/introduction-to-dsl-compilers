# Introduction to DSL Compilers

Template repository for the university course **"Introduction to DSL compilers"**.

All tasks are solved in Python. Tests are required and are an integral part of every
assignment. In addition to example-based tests, property-based tests written with the
[Hypothesis](https://hypothesis.readthedocs.io/) framework are required, so solutions
are verified by properties of the algorithms rather than hardcoded input/output pairs.

## Course format
The course is split into topics. Each topic lives in its own folder: `topic-1`, `topic-2`, and so on.

Each topic folder contains:
* `README.md` — the task description and acceptance criteria;
* a Python template file with the required function signature and an empty implementation;
* a starter test suite — **intentionally incomplete**; extending it is part of the assignment.

### Requirements for submitting homework for review
Failure to comply with any of the following rules will result in the homework not being reviewed:
* The solution is submitted as a pull request from a branch named after the topic (`topic-1`, `topic-2`, ...).
* The code runs without errors.
* Tests are implemented and extended beyond the starter suite, including Hypothesis property-based tests.
* All tests for the topic pass, both locally and in the GitHub Actions build.
* The code passes the [Ruff](https://docs.astral.sh/ruff/) lint and formatting checks (see [Code style](#code-style)).

Students may submit incomplete homework to verify assumptions, but any incompleteness
must be explicitly stated in the submission.

### Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) is forbidden for the tasks unless a topic explicitly states otherwise.** Both implementations and tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks and lecture materials to understand the algorithms.

## Property-based testing and Hypothesis
Classic example-based tests check a function against a handful of hardcoded input/output
pairs. Such tests are easy to satisfy by accident — or by hardcoding — and they only ever
cover the cases their author thought of.

**Property-based testing** takes a different approach: instead of fixed examples, you state
a *property* that must hold for **any** valid input, and the testing framework generates
hundreds of random inputs trying to find one that breaks it. For a substring search, useful
properties look like:
* if we build a text by inserting the pattern at a known position, that position must be
  among the reported occurrences;
* if the text and the pattern are built from disjoint alphabets, no occurrence may be
  reported;
* every reported index, when used to slice the text, must yield the pattern.

In this course we use [Hypothesis](https://hypothesis.readthedocs.io/), the standard
property-based testing framework for Python. You describe how to generate inputs with
*strategies* (`st.text()`, `st.integers()`, `st.lists()`, ...), attach them to a test with
the `@given` decorator, and Hypothesis runs the test on many generated inputs. When it
finds a failing input, it automatically *shrinks* it to a minimal counterexample — so a
failure is reported as, say, `text='', pattern='a'` rather than a page of random noise.

Recommended reading:
* [Hypothesis documentation](https://hypothesis.readthedocs.io/)
* [Quick start guide](https://hypothesis.readthedocs.io/en/latest/quickstart.html)
* [What is property-based testing?](https://hypothesis.works/articles/what-is-property-based-testing/)

The starter test suites in each topic are written with Hypothesis and demonstrate the
constructive style described above. They are intentionally incomplete: extending them with
your own properties is part of every assignment.

# Prerequisites
1. [Git](https://git-scm.com/downloads)
2. [uv](https://docs.astral.sh/uv/getting-started/installation/) — the Python package and project manager used in this course. You do **not** need to install Python separately: `uv` downloads and manages the required Python version automatically.
3. A [GitHub](https://github.com/) account.

# How to start
1. Create a GitHub account (if you don't already have one).
2. Set up a **private** GitHub repository.
3. Clone this course repository locally (**do not fork it**).
4. Detach the original course repository so you cannot accidentally push to it.
5. Link the local repository to your private GitHub repository and push.
6. Create a new branch for each topic.

### Create a GitHub account
Visit https://github.com/ and follow the sign-up process.
Choose a professional username, typically in the format `[First][Last]`.

### Create a new repository on GitHub
Follow this [guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).
* Ensure the repository is **private**.
* Name the repository `introduction-to-dsl-compilers` to match the original repository name.
* Do **not** initialize it with a README, `.gitignore`, or license — it must stay empty so you can push the course history into it.
* Add your instructor as a collaborator:
  * [Igor Wolkov](https://github.com/IgorWolkov)

### Clone the course repository
**Important**: Do **not** fork the repository. A fork of the (public) template cannot be made
private, and your solutions must not be publicly visible.

To clone the repository, run:
```shell
git clone https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git
cd introduction-to-dsl-compilers
```

### Verify the cloned repository
Check the remotes:
```shell
git remote -v
```
The output should be:
```shell
origin	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (fetch)
origin	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (push)
```

Check the branches:
```shell
git branch
```
The output should be:
```shell
* main
```

Install the dependencies and run a quick sanity check:
```shell
uv sync
uv run pytest --collect-only
```
`uv sync` creates a local virtual environment (`.venv/`) and installs the exact dependency
versions pinned in `uv.lock`. The second command should list the test cases without errors.

### Secure the original repository
Students are **not allowed** to push changes to the original course repository.
To prevent accidental pushes, detach the original repository from your private repository:
rename the `origin` remote and disable `push` to it.

#### Rename origin
```shell
git remote rename origin course
```
Run `git remote -v`. The output should be:
```shell
course	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (fetch)
course	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (push)
```

#### Disable pushes
Replace the push URL with a non-existent value (for example, `DISABLED`):
```shell
git remote set-url --push course DISABLED
```
Run `git remote -v`. The output should be:
```shell
course	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (fetch)
course	DISABLED (push)
```
Now `git pull course main` still works (fetching updates is allowed), but any attempt to
push to the course repository fails immediately.

### Link the local repository to your private repository
Add your private repository as the new `origin` and push:
```shell
git remote add origin https://github.com/<your GitHub account>/introduction-to-dsl-compilers.git
git branch -M main
git push -u origin main
```
Run `git remote -v`. The output should be:
```shell
course	https://github.com/Mexmath-Foundation/introduction-to-dsl-compilers.git (fetch)
course	DISABLED (push)
origin	https://github.com/<your GitHub account>/introduction-to-dsl-compilers.git (fetch)
origin	https://github.com/<your GitHub account>/introduction-to-dsl-compilers.git (push)
```

### Pull updates from the original course repository
The original course repository may be updated from time to time (new topics, fixes).
To fetch updates, run:
```shell
git checkout main
git pull course main
git push origin main
```

# Working on a topic

## New branch for each topic
Students are **not allowed** to commit any changes to the `main` branch, except in explicitly
described cases. A separate branch is required for each topic, and the branch **must** be
named exactly after the topic folder:
* `topic-1` for Topic 1;
* `topic-2` for Topic 2;
* ...
* `topic-n` for Topic n.

The naming convention is used by the GitHub Actions build to run only the tests related to
the topic you are working on: for the branch `topic-1` only the tests in the `topic-1` folder
are executed. Violating the convention leads to failed builds.

## Running tests locally
To run the tests for a specific topic:
```shell
uv run pytest topic-1
```
To run a single test file:
```shell
uv run pytest topic-1/test_naive_search.py
```
To run all tests in the repository (expected to fail until all topics are solved):
```shell
uv run pytest
```

## Code style
The project uses [Ruff](https://docs.astral.sh/ruff/) as the linter and code formatter.
The configuration lives in the `[tool.ruff]` section of [`pyproject.toml`](pyproject.toml).
Both checks are enforced in the GitHub Actions build, so run them before pushing.

### Checking the formatting
To check whether the code is properly formatted **without changing any files**, run:
```shell
uv run ruff format --check .
```
The command lists the files that would be reformatted and exits with a non-zero code
if any file is not properly formatted. This is exactly the check the CI build runs.

### Applying the formatting
To automatically reformat all files according to the project code style, run:
```shell
uv run ruff format .
```
Run it (or set up your IDE to format with Ruff on save) before every commit.

### Checking the code with the linter
To check the code for lint violations (unused imports, unsorted imports, common bug
patterns, outdated syntax, ...), run:
```shell
uv run ruff check .
```

### Fixing lint violations
Many lint violations can be fixed automatically. To apply the automatic fixes, run:
```shell
uv run ruff check --fix .
```
Violations that cannot be fixed automatically are reported with an explanation and a
rule code; look the code up in the [Ruff rules reference](https://docs.astral.sh/ruff/rules/)
to understand what to change.

### One command to rule them all
To apply the formatting, apply the automatic lint fixes, and verify both checks pass, run:
```shell
uv run ruff format . && uv run ruff check --fix .
```

## GitHub Actions build
Every push to a `topic-*` branch, every pull request, and every push to `main`
(e.g. a merged pull request) triggers the CI build
(see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)). The build:
1. Determines which topics to test:
   * on a `topic-*` branch or a pull request from one — the topic matching the branch name; the build fails if the branch does not follow the `topic-N` convention;
   * on a push to `main` — every topic folder touched by the pushed commits, so merging the `topic-1` pull request re-runs the `topic-1` tests on `main`, while still unsolved topics are not tested.
2. Installs the dependencies with `uv sync --locked`.
3. Lints and checks formatting with `uv run ruff check .` and `uv run ruff format --check .`.
4. Runs `uv run pytest <topic>` for each selected topic folder.

To replicate the CI behavior locally, run:
```shell
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest topic-<n>
```

## Repeat it every time
1. Check out the `main` branch.
2. Update the `main` branch (`git pull course main`).
3. Create or check out a local `topic-n` branch.
4. Merge the `main` branch into the local `topic-n` branch.
5. Commit all necessary changes to the local `topic-n` branch.
6. Push the changes to your private remote GitHub repository (`git push origin topic-n`).
7. Create a pull request from `topic-n` to `main` **in your private repository**.
8. Make sure the GitHub Actions build is green.
9. Assign a reviewer:
   * [Igor Wolkov](https://github.com/IgorWolkov)

# Topics
* [Topic 1: Naive Substring Search](topic-1/README.md)
* [Topic 2: Knuth–Morris–Pratt Substring Search](topic-2/README.md)
* [Topic 3: Aho–Corasick Multi-Pattern Search](topic-3/README.md)

Erowid Archetypes Project
=========================

This is an LLM-assisted analysis of the occurance of Jungian archetypes in
Salvia and DMT trips from Erowid, a website where uses submit self-reported
drug trips.

Running the Environment
-----------------------

This repository is built to run in a Docker container. You can start the
container on linux via:

```

bash start.sh emacs

```

This will start an Emacs. If you want to use RStudio instead:

```
bash start.sh rstudio

```

Running The Code
----------------

From a terminal in the container invoke Make:

```

make report.pdf

```

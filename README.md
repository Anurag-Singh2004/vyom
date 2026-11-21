# Vyom

Multi-hop RAG over India's space programme, with every retrieval stage measured.

Status: under construction. Live demo link, CI badge and demo GIF will be
added here after deployment.

## What it does and why it is hard

Vyom answers questions about India's space programme (missions, launch
vehicles, centres, people) using about 250 English Wikipedia articles. Many
questions need facts from several articles at once. These are called
multi-hop questions, and a single search often fails to find all the
required articles. Answers include citations to the passages used, and the
system refuses to answer when the evidence is weak.

(To be expanded with one worked multi-hop example.)

## Architecture

Offline: Wikipedia articles -> chunking (two variants) -> BM25 index and
dense (FAISS) index.

Online, for one question: optional decomposition into sub-questions ->
retrieval -> optional reranking -> refusal check -> generation with
citations.

(Architecture diagram and a short description of each stage to be added.)

## Results

Not yet measured. Ablation tables will be added here from the files in
eval/results/. Caveats about the small evaluation set will be listed next
to the tables.

## Design decisions

(To be written after the experiments, including techniques that did not
help.)

## How to run

(To be written: local setup and Docker.)

## How to reproduce the evaluation

(To be written: the exact commands that regenerate each results table.)

## Repository structure

(To be written once the layout is final.)

## Limitations and future work

(To be written after the experiments.)

## Licence and data attribution

The code is released under the MIT licence (see the LICENSE file).

The article text comes from English Wikipedia and is licensed under
CC BY-SA 4.0. The raw text is not stored in this repository. A script
downloads it, and each article's URL is saved in the downloaded data. The
source URL of every passage shown to a user is displayed with the answer.
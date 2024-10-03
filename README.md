# Labelizer backend

## Motivation

The purpose of this app is to provide a Tinder-like experience for labeling data triplets. An anchor is presented, and the user selects between two options to determine which one is the most "similar" to the anchor in terms of similarity. There is also a tab ("validation") to compare different iterations of the embedding model.

## Architecture

Architecture choices inspired by the FastAPI tutorial: <https://fastapi.tiangolo.com/tutorial/sql-databases/>

For finding the nearest neighbor embedding, a service based on [pgvector](https://github.com/pgvector/pgvector) has been developed.

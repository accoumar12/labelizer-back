# backend

## Architecture

Architecture choices inspired by [this FastAPI tutorial](<https://fastapi.tiangolo.com/tutorial/sql-databases/>), [Netflix Dispatch project](https://github.com/Netflix/dispatch).

## Triplets

The app will deal with two kind of triplets, which are stored in two different tables:

- The triplets located in the "triplets" table. They are the triplets coming from a single model that need to be labeled by the user of the app, to know which one of the proposition is closest to the anchor proposition, which is located at the center. They are the default triplets.
- The triplets located in the "validation triplets" table.

When we want to reference to both triplets and validation triplets, we use the reference 'all triplets'.

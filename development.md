# Development

## Getting started

### Launch the backend

```bash
cd docker
docker compose up
```

NOTE: If you see a `psycopg2.errors.UniqueViolation` or `psycopg2.OperationalError` error, do this (possibly a few times!):

```bash
docker compose down
docker compose up
```

### Launch [the frontend](https://github.com/accoumar12/labelizer-front)

```bash
npm i
npm run dev
```

### Play

- Go to `http://localhost:5173/db`.
- Upload sample data located in `test_data/test_data.zip`, in the **Upload Database** section.
- Play with the data in the **Labelling** and **Validation** tabs!

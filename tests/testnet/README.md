Borrowed from: https://github.com/eigerco/lumina/tree/main/ci

To run tests with a previous version of node, create images as follows:
```
docker compose down -v
rm -f ./credentials/*.jwt
rm -f ./credentials/*.peer
docker compose --env-file .env.v0.20.4 build
```
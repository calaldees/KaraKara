# Get Started Hosting KaraKara

```
git clone https://github.com/calaldees/karakara
cd karakara
cp .env.example .env
vim .env
docker compose up --build --pull=always -d
```

If you plan to include syncthing, note that syncthing runs without a password by default - you will want to go to http://yoursite.com/syncthing/ and set a password ASAP

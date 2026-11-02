# GitHub setup steps

1. Create an empty repository on github.com (no README, no .gitignore, no license).
2. In a terminal inside this folder run:

```bash
git init
git branch -M main
git config user.name "Your Name"
git config user.email "you@example.com"
```

3. Commit in stages (gives a meaningful history):

```bash
git add .gitignore README.md
git commit -m "Add project README and .gitignore"

git add backend
git commit -m "Add FastAPI backend with auth, chat, symptoms, medicines and history"

git add frontend
git commit -m "Add React frontend and connect it to the backend API"

git add docs
git commit -m "Add docs folder for report, manual and screenshots"
```

4. Connect and push:

```bash
git remote add origin https://github.com/<your-username>/ai-health-assistant.git
git push -u origin main
```

If asked to log in, use a Personal Access Token as the password
(GitHub > Settings > Developer settings > Personal access tokens).

# Configuration PythonAnywhere pour Yara Express

## Changements effectués

✅ **Suppression des configurations Render :**
- `Procfile` - Neutralisé (spécifique à Render/Heroku)
- `runtime.txt` - Neutralisé (spécifique à Render)

✅ **Mise à jour de `requirements.txt` :**
- ✓ Suppression de `gunicorn` (PythonAnywhere n'en a pas besoin)
- ✓ Suppression de `whitenoise` (PythonAnywhere gère le statique)
- ✓ Suppression de `dj-database-url` et `psycopg2-binary`
- ✓ Gardé : Django, Pillow, requests, django-environ

✅ **Mise à jour de `settings.py` :**
- Suppression du middleware WhiteNoise
- Suppression de la configuration Render DATABASE_URL
- Configuration SQLite par défaut
- ALLOWED_HOSTS adapté pour PythonAnywhere

✅ **Mise à jour de `.env` :**
- DEBUG=False pour la production
- ALLOWED_HOSTS configuré pour PythonAnywhere

## Steps pour déployer sur PythonAnywhere

### 1. Créer un compte PythonAnywhere
- Allez à https://www.pythonanywhere.com
- Inscrivez-vous (compte gratuit disponible)

### 2. Configuration du Web App

**Dans le dashboard PythonAnywhere :**

1. **Créer une Web App**
   - Cliquez sur "Web"
   - Sélectionnez "Add a new web app"
   - Choisissez "Manual configuration"
   - Sélectionnez Python 3.13 (ou votre version préférée)

2. **Télécharger le code**
   ```bash
   # Via Git (recommandé)
   cd ~
   git clone https://github.com/votre-repo/yaraexpress.git
   
   # Ou via Bash simple (drag & drop ou SCP)
   ```

3. **Créer un virtualenv**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.13 yaraexpress
   pip install -r ~/yaraexpress/requirements.txt
   ```

4. **Configurer les variables d'environnement**
   - Créez le fichier `.env` dans `~/yaraexpress/`
   - Copiez le contenu de `.env` (modifier les valeurs)
   - **Important :** Changez `yourusername` par votre nom d'utilisateur PythonAnywhere
   - Générez une nouvelle SECRET_KEY sécurisée

5. **Configurer le Web App**
   - Dans "Web" > Votre app > "WSGI configuration file"
   - Éditez le fichier WSGI généré automatiquement
   - Remplacez le contenu par :

```python
import os
import sys

# Add the project directory to sys.path
project_home = '/home/yourusername/yaraexpress'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'yaraexpress.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. **Configurer les fichiers statiques**
   - Dans "Web" > Votre app > "Static files"
   - Ajouter :
     ```
     URL: /static/
     Directory: /home/yourusername/yaraexpress/staticfiles
     ```
   - Ajouter aussi :
     ```
     URL: /media/
     Directory: /home/yourusername/yaraexpress/media
     ```

7. **Initialiser la base de données**
   ```bash
   # Activez le virtualenv
   workon yaraexpress
   
   # Appliquez les migrations
   cd ~/yaraexpress
   python manage.py migrate
   
   # Collectez les fichiers statiques
   python manage.py collectstatic --noinput
   
   # Créez un superuser (admin)
   python manage.py createsuperuser
   ```

8. **Rechargez l'application**
   - Dans le dashboard, cliquez sur le bouton "Reload" pour votre Web App

## Vérification

- Visitez `https://yourusername.pythonanywhere.com`
- Admin : `https://yourusername.pythonanywhere.com/admin`
- Vérifiez les fichiers statiques (CSS, JS, images)

## Dépannage

### Les fichiers statiques ne s'affichent pas
```bash
# Recollectez les fichiers statiques
python manage.py collectstatic --noinput --clear
```

### La base de données n'existe pas
```bash
python manage.py migrate
```

### Erreurs de permission
- Vérifiez que les permissions des fichiers sont correctes
- Utilisez `chmod 755` si nécessaire

## Notes importantes

- Gardez votre SECRET_KEY secret - ne le committez jamais
- Testez localement avant de déployer : `python manage.py runserver`
- Mettez à jour `ALLOWED_HOSTS` dans `.env` si vous changez de domaine
- PythonAnywhere fournit un certificat SSL gratuit

## Liens utiles

- [Documentation PythonAnywhere Django](https://www.pythonanywhere.com/docs/web_app/Django)
- [Configuration statiques](https://www.pythonanywhere.com/docs/web_app/static_files)
- [Variables d'environnement](https://www.pythonanywhere.com/docs/web_app/SettingEnvvars)

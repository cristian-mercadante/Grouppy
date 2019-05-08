# NOTE

## Database
### SQLite + creazione DB
```
# Creare database
sqlite3 database.db
.tables
.exit

# Caricare le tabelle da modelli
## Fare dentro terminale python
from grouppy import db
db.create_all()
exit()
```

### Flask Migrate
```
# Se fatto per la prima volta:
python run.py db init

# Altrimenti genera la migrazione
python run.py db migrate

# Effettua la migrazione
python run.py db upgrade
```
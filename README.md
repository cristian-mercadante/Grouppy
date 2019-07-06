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
python migrate.py db init

# Altrimenti genera la migrazione
python migrate.py db migrate

# Effettua la migrazione
python migrate.py db upgrade
```
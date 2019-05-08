from grouppy import app, db

if __name__ == '__main__':
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()

from website import db, create_app
app = create_app()
ctx = app.app_context()
ctx.push()
# Drop all tables
db.drop_all()
# Reset the tables
db.create_all()
ctx.pop()
quit()

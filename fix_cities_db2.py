content = open('scripts/build_cities_db.py', 'r', encoding='utf-8').read()

# Disable foreign keys during bulk insert, re-enable after
old = '        con.executescript(SCHEMA)'
new = '''        con.executescript(SCHEMA)
        con.execute("PRAGMA foreign_keys = OFF")'''

content = content.replace(old, new)

# Re-enable after commit
old = '        con.commit()\n\n        # Optimize the DB'
new = '''        con.commit()
        con.execute("PRAGMA foreign_keys = ON")

        # Optimize the DB'''

content = content.replace(old, new)

open('scripts/build_cities_db.py', 'w', encoding='utf-8').write(content)
print('Fixed!')

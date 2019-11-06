
# savis

> SQLAlchemy Entity Relationship diagrams basing just on model definitions

savis in a nutshell
-------------------

This is a pet-project that allows you to visualize your models relations between them without running a database.

If you're looking for solution that can import data from running database you might want to try [eralchemy](https://github.com/Alexis-benoist/eralchemy). BTW this tool is supposed to be used in tandem with eralchemy.

using
-----
Assuming following simple example.
```python
class User(Base):
    __tablename__ = 'user'

    id = Column(String(32), primary_key=True)
    type = Column(Enum(UserType))


class UserProfile(Base):
    __tablename__ = 'user_profile'

    user = Column(ForeignKey(User.id), primary_key=True)
    display_name = Column(String(128))
    email = Column(String(80))
```
Running:
```bash
./savis.py -o diagram.er -e '*async*' /repo/project/
eralchemy -i diagram.er -o diagram.png
```

Gives
![ERD](/test/models.erd.png)

raison d'être
-------------

What I wanted was to write definitions of models and relations <strong>only in single place</strong> and to review resulting ER diagram with minimal fuss.

This single place seems to be... SQLAlchemy model definitions on their own!

* online tools require you to put your data online and also have their own
  representations.
* eralchemy is decent, but it requires either custom defintion format or
  running a database. When you make rapid changes this requires automation
  or other solution to streamline the work. Anyways.. why running database
  if you only want a diagram and all of the information is already in
  Python source files?


how does it work?
-----------------

It simply parses Python source files and looks for SQLAlchemy model definitions. For each definition it will create Markdown representation with all the fields (including foreign keys).

Then, you can pass generated file to eralchemy.


limitations
-----------

I'm not sure whether all of possible fields and configurations are possible. This project implements everything I wanted to see. Certainly there are uncovered areas. Patches welcome!

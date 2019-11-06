import pathlib
from savis import main

EXAMPLE_MODELS = '''
class User(Base):
    __tablename__ = 'user'

    id = Column(String(32), primary_key=True)
    type = Column(Enum(UserType))


class UserProfile(Base):
    __tablename__ = 'user_profile'

    user = Column(ForeignKey(User.id), primary_key=True)
    display_name = Column(String(128))
    email = Column(String(80))
'''

EXAMPLE_EXPECTED_MD = '''[User]
*id {label:"String"}
type {label:"Enum"}


[UserProfile]
*user {label:"ForeignKey(User)"}
display_name {label:"String"}
email {label:"String"}


User 1--1 UserProfile
'''

def test_example(capsys, fs):
    file_path = '/models.py'
    fs.create_file(file_path, contents=EXAMPLE_MODELS)
    main(pathlib.PosixPath('/'), None, 'md')
    assert capsys.readouterr().out == EXAMPLE_EXPECTED_MD

class User(Base):
    __tablename__ = 'user'

    id = Column(String(32), primary_key=True)
    type = Column(Enum(UserType))


class UserProfile(Base):
    __tablename__ = 'user_profile'

    user = Column(ForeignKey(User.id), primary_key=True)
    display_name = Column(String(128))
    email = Column(String(80))

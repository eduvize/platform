from sqlmodel import Field, Relationship, SQLModel
import domain

class InstructorBase(SQLModel):
    name: str           = Field(default=None)
    avatar_url: str     = Field(default=None)

class Instructor(InstructorBase, table=True):
    __tablename__ = "user_instructors"
    
    id: int                                 = Field(default=None, primary_key=True)
    user_id: int                            = Field(default=None, foreign_key="users.id")
    
    user: "domain.schema.user.User"         = Relationship(back_populates="instructor")
"""UserTableSeeder Seeder."""

from masoniteorm.seeds import Seeder
from tests.integrations.app.User import User


class UserTableSeeder(Seeder):
    def run(self):
        """Run the database seeds."""
        User.create(
            {
                "name": "Joe",
                "email": "idmann509@gmail.com",
                # bcrypt hash of "secret" so auth attempts in tests succeed
                "password": "$2b$12$BKR8wrzDwn0xmRX/j45FK.OdLD3W09mqIsAIIqefGv88T.vfuKdui",
                "phone": "+123456789",
            }
        )

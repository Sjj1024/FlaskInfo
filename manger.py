from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models


app = create_app("development")
# 设置manger管理对象
manager = Manager(app)
# 配置数据库迁移设置,关联app和db
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()

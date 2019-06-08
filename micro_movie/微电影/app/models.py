from sqlalchemy.dialects.mysql import pymysql

from app import db
import datetime



#会员
class User(db.Model):
    __tablename__="user"
    #编号
    id=db.Column(db.Integer,primary_key=True)
    #昵称 unique = True唯一的
    name=db.Column(db.String(100),unique=True)
    # 密码
    pwd=db.Column(db.String(100))
    # 邮箱
    email=db.Column(db.String(100),unique=True)
    # 电话
    phone=db.Column(db.String(11),unique=True)
    # 个人简介
    info=db.Column(db.Text)
    #头像 链接
    face=db.Column(db.String(255),unique=True)
    #注册时间
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    #唯一标志符
    uuid=db.Column(db.String(255),unique=True)
    #状态
    status=db.Column(db.Integer,default=1)
    userlogs=db.relationship('Userlog',backref='user')  #会员日志外键关联
    comments=db.relationship('Comment',backref='user')  #评论关联
    movicecols = db.relationship('Movicecol', backref='user')  # 电影收藏关联

    # 返回方法
    def __repr__(self):
        return "<User %r>"%self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)

# class Cold(db.Model):
#     __tablename__ = "cold"
#     id=db.Column(db.Integer,primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#会员登陆日志
class Userlog(db.Model):
    __tablename__ = "userlog"
    # 日志编号
    id=db.Column(db.Integer,primary_key=True)
    #会员id 外键
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #登陆ip
    ip=db.Column(db.String(100))
    #登录时间
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Userlog %r >"%self.id



#电影
class Movie(db.Model):
    __tablename__="movie"
    #编号
    id=db.Column(db.Integer,primary_key=True)
    #标题
    title=db.Column(db.String(255),unique=True)
    #地址
    url=db.Column(db.String(255),unique=True)
    #信息
    info=db.Column(db.Text)
    #封面
    logo=db.Column(db.String(255),unique=True)
    #星级
    star=db.Column(db.SmallInteger)
    #播放量
    playnum=db.Column(db.BigInteger)
    #评论量
    commentnum=db.Column(db.BigInteger)
    #标签
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    #上映地区
    area=db.Column(db.String(255))
    #上映时间
    release_time=db.Column(db.Date)
    #电影长度
    length=db.Column(db.String(100))
    #添加时间
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    comment = db.relationship('Comment', backref='movie')  # 评论关联
    movicecols = db.relationship('Movicecol', backref='movie')  # 收藏关联

    def __repr__(self):
        return "<Movie %r>"%self.title


#电影标签
class Tag(db.Model):
    __tablename__ = "tag"
    #编号
    id=db.Column(db.Integer,primary_key=True)
    #标题
    name=db.Column(db.String(100),unique=True)
    #添加时间
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)
    #外键关联电影
    movies = db.relationship('Movie', backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name




#预告模型
class Preview(db.Model):
    __tablename__="preview"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    title = db.Column(db.String(255), unique=True)
    #封面
    logo=db.Column(db.String(255),unique=True)
    #添加时间
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Preview %r>" % self.name

#评论
class Comment(db.Model):
    __tablename__='comment'
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    #内容
    content=db.Column(db.Text)
    movie_id=db.Column(db.Integer,db.ForeignKey('movie.id')) #所属电影
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))#所属用户
    addtime=db.Column(db.DateTime,index=True,default=datetime.datetime.now)

    def __repr__(self):
        return "<Conmment %r>" % self.id


#电影收藏
class Movicecol(db.Model):
    __tablename__ = 'movicecol'
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    #添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)

    def __repr__(self):
        return "<Moviecol %r>" % self.id

#权限
class Auth(db.Model):
    __tablename__='auto'
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    name = db.Column(db.String(100), unique=True)
    # 地址
    url = db.Column(db.String(255), unique=True)
    # 添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)

    def __repr__(self):
        return "<Auth %r>" % self.name

# 角色
class Role(db.Model):
    __tablename__ = 'role'
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    name = db.Column(db.String(100), unique=True)
    #权限列表
    auths=db.Column(db.String(600))
    # 添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    admins=db.relationship("Admin",backref='role')#管理员外键关系关联
    def __repr__(self):
        return "<Role %r>" % self.name

#管理员
class Admin(db.Model):
    __tablename__ = "admin"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 管理员账户 unique = True唯一的
    name = db.Column(db.String(100), unique=True)
    # 管理员密码
    pwd = db.Column(db.String(100))
    is_super=db.Column(db.SmallInteger)
    #所属角色
    role_id=db.Column(db.Integer,db.ForeignKey("role.id"))
    # 添加时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    #管理员登陆外键关系关联
    adminlogs=db.relationship('Adminlog',backref='admin')
    # 管理员外键关系关联
    oplogs = db.relationship('Oplog', backref='admin')



    def __repr__(self):
        return "<Admin %r>" % self.name

    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

#管理员登陆日志
class Adminlog(db.Model):
    __tablename__ = "adminlog"
    # 日志编号
    id = db.Column(db.Integer, primary_key=True)
    # 会员id 外键
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    # 登陆ip
    ip = db.Column(db.String(100))
    # 登录时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)

    def __repr__(self):
        return "<Adminlog %r >" % self.id


#操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    # 日志编号
    id = db.Column(db.Integer, primary_key=True)
    # 会员id 外键
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    # 登陆ip
    ip = db.Column(db.String(100))
    #原因
    reson=db.Column(db.String(600))
    # 登录时间
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now)

    def __repr__(self):
        return "<Oplog %r >" % self.id


if __name__ == '__main__':

    from werkzeug.security import generate_password_hash

    # role=Role(
    #     name="超级管理员",
    #     auths="",
    # )
    # db.session.add(role)
    # db.session.commit()
    # admin=Admin(
    #     name='root',
    #     pwd=generate_password_hash('root'),
    #     is_super=0,
    #     role_id=1,
    # )
    # db.session.add(admin)
    # db.session.commit()


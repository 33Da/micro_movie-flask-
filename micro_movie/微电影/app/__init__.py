from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app=Flask(__name__)
#设置数据库链接  'mysql+pymysql://用户名称:密码@localhost:端口/数据库名称'
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:root@127.0.0.1:3306/wei_movie"
#默认就为true
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True

#设置SECRET_KEY,csrf设置
app.config['SECRET_KEY']='e4966b2e2e7146f38dc9dab24fc25838'

app.config['UP_DIR']=os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/upload/')
app.config['UPUSER_DIR']=os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/upload/user/')


db=SQLAlchemy(app)
app.debug=True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

# 注册蓝图
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix="/admin")



#404
@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"),404


from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect(app)

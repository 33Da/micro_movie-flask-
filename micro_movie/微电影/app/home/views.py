import json
import os
import uuid

from flask_wtf import csrf
from werkzeug.utils import secure_filename

from . import home
from flask import render_template,redirect,url_for,flash,session,request
from app.home.forms import RegistForm,LoginForm,UserForm,Pwdform,CommentForm
from app.models import User,Userlog,Tag,Movie,Comment,Movicecol
from werkzeug.security import generate_password_hash
from app import db,app
from datetime import datetime
from functools import wraps


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H&M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


def home_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function



@home.route("/login/",methods=['POST',"GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data['name']).first()
        if user ==None :
            flash("密码或账号错误",'err')
            return redirect(url_for("home.login"))
        if not user.check_pwd(data['pwd']):
            flash('密码或账号错误','err')
            return redirect(url_for("home.login"))
        if user.status==0:
            flash('账号被冻结','err')
        session['username'] = data['name']
        session['user_id']=user.id
        userlog=Userlog(
            user_id=user.id,
            # 获取ip
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('home.index',page=1))

    username = get_username()
    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }

    return render_template("home/login.html",form=form,context=context)


@home.route("/logout/")
def logout():
    session.pop('username', None)
    return redirect(url_for("home.login"))


@home.route("/regist/",methods=["POST",'GET'])
def regist():
    form=RegistForm()

    if form.validate_on_submit():
        data=form.data

        user_count=User.query.filter_by(name=data['name']).count()
        if user_count==1:
            flash('该用户已重复','err')

            return redirect(url_for('home.regist'))

        user = User(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            email=data['email'],
            phone=data['phone'],
            uuid=uuid.uuid4().hex,

        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("home.login"))
    username = get_username()
    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/regist.html",form=form,context=context)


#会员中心
@home.route("/user/",methods=['GET','POST'])
@home_login_req
def user():
    username = get_username()
    form=UserForm()
    user=User.query.get_or_404(int(session['user_id']))
    if request.method=="GET":
        form.name.data=user.name
        form.email.data=user.email
        form.info.data=user.info
        form.face.data=user.face
        form.phone.data=user.phone

    if form.validate_on_submit():
        data=form.data
        if not os.path.exists(app.config['UPUSER_DIR']):
            os.makedirs(app.config["UPUSER_DIR"])
            os.chmod(app.config["UPUSER_DIR"],os.O_RDWR)

        if form.face.data.filename != None:
            file_url = secure_filename(form.face.data.filename)
            url = change_filename(file_url)
            form.face.data.save(app.config["UPUSER_DIR"] + url)

        name_count=User.query.filter_by(name=data['name']).count()
        if name_count==1 and user.name != data['name']:
            flash('昵称重复','err')
            return redirect(url_for('home.user'))

        phone_count = User.query.filter_by(phone=data['phone']).count()
        if phone_count == 1 and user.phone != data['phone']:
            flash('手机号重复', 'err')
            return redirect(url_for('home.user'))

        email_count = User.query.filter_by(email=data['email']).count()
        if email_count == 1 and user.email != data['email']:
            flash('邮箱重复', 'err')
            return redirect(url_for('home.user'))

        user.name=data['name']
        user.phone=data['phone']
        user.face = url
        user.email=data['email']
        user.info=data['info']
        db.session.add(user)
        db.session.commit()
        flash('修改成功','ok')
        return redirect(url_for('home.user'))

    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/user/user.html",context=context,form=form,user=user)

# 修改密码
@home.route("/pwd/",methods=['POST',"GET"])
@home_login_req
def pwd():
    username=get_username()
    form=Pwdform()
    user = User.query.get_or_404(int(session['user_id']))
    if form.validate_on_submit():
        data = form.data

        if not user.check_pwd(data['pwd']):
            flash('旧密码错误', 'err')
            return redirect(url_for("home.pwd"))

        user.pwd = generate_password_hash(data['newpwd'])
        db.session.add(user)
        db.session.commit()
        flash('修改成功', 'ok')
        return redirect(url_for('home.pwd'))
    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/user/pwd.html",context=context,form=form)

#评论
@home.route("/comment/<int:page>")
@home_login_req
def comment(page=1):
    username = get_username()

    page_data = Comment.query.filter_by(
        user_id=int(session['user_id'])
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/user/comments.html",context=context,user=user,page=page_data)

#登陆日志
@home.route("/loginlog/<int:page>")
@home_login_req
def loginlog(page):
    username = get_username()
    if page == None:
        page = 1

    page_data = Userlog.query.filter_by(
            user_id=int(session['user_id'])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/user/loginlog.html",context=context,page=page_data)

#电影收藏
@home.route("/moviecol_add/",methods=['GET'])
@home_login_req
def moviecol_add():
    username = get_username()
    uid=request.args.get('uid','')
    mid=request.args.get('mid','')
    moviecol=Movicecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid),
    ).count()
    if moviecol==1:
        data=dict(ok=0)
    else:
        moviecol=Movicecol(
            user_id=int(uid),
            movie_id=int(mid),

        )
        db.session.add(moviecol)
        db.session.commit()
        data=dict(ok=1)
    return json.dumps(data)

    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }

    return render_template("home/user/moviecol.html",context=context)

#电影收藏
@home.route("/moviecol/<int:page>",methods=['GET'])
@home_login_req
def moviecol(page=1):
    username = get_username()


    page_data = Movicecol.query.filter_by(
        user_id=int(session['user_id'])
    ).order_by(
        Movicecol.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目


    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }

    return render_template("home/user/moviecol.html",context=context,page=page_data)


# 主页
@home.route("/<int:page>/")
def index(page=1):

    tags=Tag.query.all()

    page_data=Movie.query


    tid=request.args.get('tid',0)
    if int(tid)!=0:
        page_data=page_data.filter_by(tag_id=int(tid))

    star=request.args.get('star',0)
    if int(star)!=0:
        page_data=page_data.filter_by(star=int(star))

    time=request.args.get('time',0)
    if int(time)!=0:
        if int(time) ==1:
            page_data=page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )

    # 播放数量
    pm=request.args.get('pm',0)
    if int(pm)!=0:
        if int(pm) ==1:
            page_data=page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论数量
    cm=request.args.get('cm',0)
    if int(cm) !=0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.comment.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.comment.asc()
            )

    page_data=page_data.paginate(page=page,per_page=10)

    # 构建一个参数字典
    p=dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )

    username=get_username()


    if username != None:
        context={
           'login':username
        }
    else:
        context={
            'login':" "
        }
    return render_template("home/index.html",context=context,tags=tags,p=p,page=page_data)

#动画
@home.route("/animation/")
def animation():
    return render_template("home/animation.html")


#搜索
@home.route("/search/<int:page>")
def search(page=1):

    username = get_username()
    key=request.args.get('key'," ")
    count = Movie.query.filter(
        # 模糊匹配
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).count()

    page_data=Movie.query.filter(
        # 模糊匹配
        Movie.title.ilike('%'+key+'%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page,per_page=10)
    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }
    return render_template("home/search.html",context=context,key=key,page=page_data,count=count)


# 播放
@home.route("/play/<int:id>/<int:page>",methods=['GET','POST'])
def play(id=None,page=1):
    username = get_username()
    movie = Movie.query.get_or_404(int(id))
    movie.playnum=movie.playnum+1
    page_data= Comment.query.join(
        Movie
    ).filter(
        Movie.id==movie.id,

    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page,per_page=10)

    form=CommentForm()
    if 'username' in session and form.validate_on_submit():
        data=form.data
        comment=Comment(
            content=data['content'],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum=movie.commentnum+1
        db.session.add(movie)
        db.session.commit()
        flash("评论成功",'ok')
        return redirect(url_for('home.play',id=movie.id,page=1))

    db.session.add(movie)
    db.session.commit()

    if username != None:
        context = {
            'login': username
        }
    else:
        context = {
            'login': " "
        }


    return render_template("home/play.html",movie=movie,context=context,form=form,page=page_data)


#弹幕播放
# @home.route("/play/<int:id>/<int:page>",methods=['GET','POST'])
# def dplay(id=None,page=1):
#     username = get_username()
#     movie = Movie.query.get_or_404(int(id))
#     movie.playnum=movie.playnum+1
#     page_data= Comment.query.join(
#         Movie
#     ).filter(
#         Movie.id==movie.id,
#
#     ).order_by(
#         Comment.addtime.desc()
#     ).paginate(page=page,per_page=10)
#
#     form=CommentForm()
#     if 'username' in session and form.validate_on_submit():
#         data=form.data
#         comment=Comment(
#             content=data['content'],
#             movie_id=movie.id,
#             user_id=session["user_id"]
#         )
#         db.session.add(comment)
#         db.session.commit()
#         movie.commentnum=movie.commentnum+1
#         db.session.add(movie)
#         db.session.commit()
#         flash("评论成功",'ok')
#         return redirect(url_for('home.play',id=movie.id,page=1))
#
#     db.session.add(movie)
#     db.session.commit()
#
#     if username != None:
#         context = {
#             'login': username
#         }
#     else:
#         context = {
#             'login': " "
#         }
#
#
#     return render_template("home/play.html",movie=movie,context=context,form=form,page=page_data)


# 获取用户名
def get_username():
    username = session.get('username')
    if username is None:
        return None
    else:
        return username

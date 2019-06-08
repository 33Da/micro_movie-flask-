from flask.json import jsonify

from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm,RegistAdminForm,AuthForm,RoleForm,Pwdform
from app.models import Admin, Tag, Movie, Preview,User,Comment,Oplog,Adminlog,Userlog,Auth,Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash
#
# 登陆权限装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

#管理权限装饰器
def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 联合查询()
        #  找Admin表中是哪个admin登陆且找到他的role，再从Role表中找到这个admin,返回对应的admin
        admin=Admin.query.join(
            Role
        ).filter(
            Admin.id == session['admin_id'],
            Role.id == Admin.role_id,

        ).first()
        if admin.is_super==1:
            auths = admin.role.auths

            auths = list(map(lambda v: int(v), auths.split(',')))
            # 查询出全部的权限
            auths_list = Auth.query.all()
            # 匹配出能访问的url
            urls = [v.url for v in auths_list for val in auths if val == v.id]
            rule = request.url_rule
            print('url', rule)
            # 要访问的页面不再urls里的就没有权限
            if str(rule) not in urls:
                return redirect(url_for('admin.index'))
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs)

    return decorated_function

# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H&M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 首页
@admin.route("/")
@admin_login_req
def index():
    username = get_username()
    context = {
        'username': username
    }
    return render_template('admin/index.html', context=context)


# 账号验证
@admin.route("/account_handle/", methods=["POST"])
def account_handle():
    account = request.form.get('account')
    print(account)
    admin = Admin.query.filter_by(name=account).count()
    print(admin)
    if admin == 0:
        return jsonify({"error": 1})
    else:
        return jsonify({'error': 0})


# 登陆
@admin.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if admin ==None:
            flash('密码或账号错误')
        if not admin.check_pwd(data['pwd']):
            flash('密码或账号错误')
            return redirect(url_for("admin.login"))
        session['admin'] = data['account']
        session['admin_id']=admin.id
        adminlog = Adminlog(
            admin_id=admin.id,
            # 获取ip
            ip=request.remote_addr
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('admin.index'))

    return render_template('admin/login.html', form=form)


# 登出
@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop('account', None)
    session.pop('admin_id',None)
    return redirect(url_for("admin.login"))




# 添加标签
@admin.route("/tag/add/", methods=["POST", "GET"])
@admin_login_req
@admin_auth
def tag_add():
    form = TagForm()
    username = get_username()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data['name']).count()

        if tag == 1:
            flash('标签已存在', 'err')
            return redirect(url_for('admin.tag_add'))
        else:
            tag = Tag(name=data['name'])
            db.session.add(tag)

            oplog=Oplog(
                ip=request.remote_addr,
                admin_id=session["admin_id"],
                reson='添加标签'+'<'+data['name']+'>',


            )
            db.session.add(oplog)
            db.session.commit()
            flash('添加成功', 'ok')
            return redirect(url_for('admin.tag_add'))

    context = {
        'username': username
    }
    return render_template("admin/tag_add.html", form=form, context=context)


# 标签list
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
@admin_auth
def tag_list(page=None):
    if page == None:
        page = 1
    # 按时间排序
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    # 分页
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/tag_list.html", page=page_data, context=context)


# 删除标签
@admin_login_req
@admin_auth
@admin.route('/tag/del/<int:id>/', methods=["GET"])
def delete_tag(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()  # 查找错误404
    username = get_username()
    admin = Admin.query.filter_by(name=username).first()
    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='删除标签'+'<'+tag.name+'>',

    )
    db.session.add(oplog)
    db.session.delete(tag)
    db.session.commit()
    flash('删除成功', "ok")


    return redirect(url_for('admin.tag_list', page=1))


# 编辑标签
@admin_login_req
@admin_auth
@admin.route('/tag/edit/<int:id>/', methods=["POST", "GET"])
def edit_tag(id=None):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    username = get_username()
    admin = Admin.query.filter_by(name=username).first()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag.name != data['name'] and tag_count == 1:
            flash('标签已存在', 'err')
            return redirect(url_for('admin.tag_list', page=1))
        else:
            tag.name = data['name']
            db.session.add(tag)

            oplog = Oplog(
                ip=request.remote_addr,
                admin_id=session["admin_id"],
                reson='编辑标签' + '<' + tag.name + '>',

            )
            db.session.add(oplog)

            db.session.commit()
            flash('修改成功', 'ok')
            return redirect(url_for('admin.tag_list', page=1))

    context = {
        'username': username
    }
    return render_template("admin/tag_edit.html", form=form, context=context)


# 添加电影
@admin.route("/movie_add/", methods=["GET", "POST"])
@admin_login_req
@admin_auth
def movie_add():
    form = MovieForm()

    username = get_username()


    if form.validate_on_submit():
        data = form.data

        # 变成一个安全的名称
        file_url = secure_filename(form.url.data.filename)

        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')

        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 保存
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            playnum=0,
            commentnum=0,
            star=int(data['star']),
            tag_id=int(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length'],

        )
        db.session.add(movie)

        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='添加电影' + '<' + data['title'] + '>',

        )
        db.session.add(oplog)

        db.session.commit()
        flash('添加电影成功', 'ok')
        return redirect((url_for('admin.movie_add')))
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/movie_add.html", form=form, context=context)


# 电影列表
@admin.route("/movie_list/<int:page>", methods=["GET"])
@admin_login_req
@admin_auth
def movie_list(page):
    if page == None:
        page = 1
    # 按时间排序
    page_data = Movie.query.order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    # 分页

    username = get_username()
    context = {
        'username': username,
    }
    return render_template("admin/movie_list.html", page=page_data, context=context)


# 删除标签
@admin_login_req
@admin_auth
@admin.route('/movie/del/<int:id>/', methods=["GET"])
def delete_movie(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()  # 查找错误404
    db.session.delete(movie)

    username = get_username()
    admin = Admin.query.filter_by(name=username).first()

    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='删除电影' + '<' + movie.title + '>',

    )
    db.session.add(oplog)
    db.session.commit()
    flash('删除成功', "ok")

    return redirect(url_for('admin.movie_list', page=1))


# 编辑电影
@admin_login_req
@admin_auth
@admin.route('/movie/edit/<int:id>/', methods=["POST", "GET"])
def edit_movie(id=None):
    form = MovieForm()

    movie = Movie.query.get_or_404(int(id))

    username = get_username()
    admin = Admin.query.filter_by(name=username).first()


    if request.method == 'GET':
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star

    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data['title']).count()
        if movie.title != data['title'] and movie_count == 1:
            flash('标签已存在', 'err')
            return redirect(url_for('admin.tag_list', page=1))

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')


        if form.url.data.filename != None:
            file_url = secure_filename(form.url.data.filename)
            url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + url)

        if form.logo.data.filename != None:
            file_logo = secure_filename(form.logo.data.filename)
            logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + logo)

        # 保存
        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.info = data['info']
        movie.title = data['title']
        movie.length = data['length']
        movie.area = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)

        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='删除电影' + '<' + movie.title + '>',

        )
        db.session.add(oplog)



        db.session.commit()
        flash('修改成功', 'ok')



        return redirect(url_for('admin.movie_list', page=1))

    context = {
        'username': username
    }
    return render_template("admin/movie_edit.html", form=form, movie=movie, context=context)


# 添加预告
@admin.route("/preview_add/", methods=["POST", 'GET'])
@admin_login_req
@admin_auth
def preview_add():
    form = PreviewForm()

    if form.validate_on_submit():

        data = form.data
        # 变成一个安全的名称
        file_logo = secure_filename(form.logo.data.filename)

        # 如果没有这个文件夹
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')

        logo = change_filename(file_logo)

        # 保存
        form.logo.data.save(app.config["UP_DIR"] + logo)

        preview = Preview(
            title=data['title'],
            logo=logo,

        )
        db.session.add(preview)

        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='添加预告' + '<' + preview.title + '>',

        )
        db.session.add(oplog)
        db.session.commit()
        flash('添加电影预告成功', 'ok')
        return redirect((url_for('admin.preview_add')))
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/preview_add.html", form=form, context=context)

# 删除预告
@admin.route("/preview_del/<int:id>", methods=['GET'])
@admin_login_req
@admin_auth
def preview_del(id=None):
    preview = Preview.query.filter_by(id=id).first_or_404()  # 查找错误404
    db.session.delete(preview)

    username = get_username()
    admin = Admin.query.filter_by(name=username).first()

    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='删除预告' + '<' + preview.title + '>',

    )
    db.session.add(oplog)
    db.session.commit()
    flash('删除成功', "ok")

    return redirect(url_for('admin.preview_list', page=1))

# 编辑预告
@admin.route("/preview_edit/<int:id>" ,methods=["GET",'POST'])
@admin_login_req
@admin_auth
def preview_edit(id):
    form = PreviewForm()

    preview = Preview.query.get_or_404(int(id))

    username = get_username()
    admin = Admin.query.filter_by(name=username).first()

    if request.method == 'GET':
        form.title.data = preview.title
        form.logo.data = preview.logo


    if form.validate_on_submit():
        data = form.data
        preview_count = preview.query.filter_by(title=data['title']).count()
        if preview.title != data['title'] and preview_count == 1:
            flash('标签已存在', 'err')
            return redirect(url_for('admin.preview_list', page=1))

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')

        if form.logo.data.filename != None:
            file_url = secure_filename(form.logo.data.filename)
            url = change_filename(file_url)
            form.logo.data.save(app.config["UP_DIR"] + url)



        # 保存
        preview.title = data['title']


        db.session.add(preview)

        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='编辑预告' + '<' + preview.title + '>',

        )
        db.session.add(oplog)

        db.session.commit()
        flash('修改成功', 'ok')

        return redirect(url_for('admin.preview_list', page=1))

    context = {
        'username': username
    }
    return render_template("admin/preview_edit.html", form=form, preview=preview, context=context)



# 预告列表
@admin.route("/preview_list/<int:page>" ,methods=["GET"])
@admin_login_req
@admin_auth
def preview_list(page):
    if page == None:
        page = 1
    # 按时间排序
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/preview_list.html", context=context,page=page_data)


# 冻结会员
@admin.route("/user_stop/<int:id>")
@admin_login_req
@admin_auth
def user_stop(id):
    user=User.query.filter_by(id=id).first_or_404()
    print(type(user.status))

    user.status = 0
    db.session.add(user)

    oplog = Oplog(
       ip=request.remote_addr,
       admin_id=session["admin_id"],
        reson='冻结会员' + '<' + user.name + '>',

        )
    db.session.add(oplog)
    db.session.commit()


    username = get_username()
    context = {
        'username': username
    }
    return redirect(url_for('admin.user_list', page=1))

#解冻
@admin.route("/user_ok/<int:id>")
@admin_login_req
@admin_auth
def user_ok(id):
    user=User.query.filter_by(id=id).first_or_404()
    user.status = 1
    db.session.add(user)

    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='解冻会员' + '<' + user.name + '>',

    )
    db.session.add(oplog)
    db.session.commit()


    username = get_username()
    context = {
        'username': username
    }
    return redirect(url_for('admin.user_list', page=1))

# 查看会员
@admin.route("/user_view/<int:id>")
@admin_login_req
@admin_auth
def user_view(id):
    user=User.query.filter_by(id=id).first_or_404()


    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/user_view.html",context=context,user=user)


# 会员列表
@admin.route("/user_list/<int:page>",methods=['GET'])
@admin_login_req
@admin_auth
def user_list(page):
    if page == None:
        page = 1
    # 按时间排序
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/user_list.html",context=context,page=page_data)

#删除会员
@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
@admin_auth
def user_del(id=None):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)

    #

    flash("删除会员成功！", "ok")
    oplog = Oplog(
        admin_id=session["admin_id"],
        ip=request.remote_addr,
        reason="删除会员：%s" % user.name
    )
    db.session.add(oplog)
    db.session.commit()
    return redirect(url_for("admin.user_list", page=1))


# 评论列表
@admin.route("/comment_list/<int:page>")
@admin_login_req
@admin_auth
def comment_list(page):
    if page == None:
        page = 1
    # 按时间排序
    page_data = Comment.query.order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/comment_list.html",context=context,page=page_data)


# 收藏列表
@admin.route("/movicecol_list/<int:page>")
@admin_login_req
@admin_auth
def movicecol_list(page):
    if page == None:
        page = 1
        # 按时间排序
    page_data = Comment.query.order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/movicecol_list.html",context=context,page=page_data)


# 操作日志
@admin.route("/oplog_list/<int:page>")
@admin_login_req
@admin_auth
def oplog_list(page):
    if page == None:
        page = 1
        # 按时间排序
    page_data = Oplog.query.order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目



    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/oplog_list.html",context=context,page=page_data)


# 管理员登陆日志
@admin.route("/adminlog_list/<int:page>")
@admin_login_req
@admin_auth
def adminlog_list(page):
    if page == None:
        page = 1
    page_data=Adminlog.query.order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    username = get_username()

    context = {
        'username': username
    }
    return render_template("admin/adminlog_list.html",context=context,page=page_data)


# 会员登陆日志
@admin.route("/userlog_list/<int:page>")
@admin_login_req
@admin_auth
def userlog_list(page):
    if page is None:
        page=1
    page_data = Userlog.query.order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/userlog_list.html",context=context,page=page_data)


# 添加权限
@admin.route("/auth_add/",methods=['GET','POST'])
@admin_login_req
@admin_auth
def auth_add():
    form=AuthForm()
    if form.validate_on_submit():
        data=form.data
        auth_count=Auth.query.filter_by(name=data['name']).count()
        if auth_count==1:
            flash('权限已存在','err')
            return redirect(url_for('admin.auth_add'))
        auth=Auth(
            name=data['name'],
            url=data['url'],
        )
        db.session.add(auth)


        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='添加权限' + '<' + auth.name + '>',

        )
        db.session.add(oplog)

        db.session.commit()
        flash('添加成功','ok')
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/auth_add.html",context=context,form=form)


# 权限列表
@admin.route("/auth_list/<int:page>")
@admin_login_req
def auth_list(page):
    if page is None:
        page=1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目

    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/auth_list.html",context=context,page=page_data)


#删除权限
@admin.route("/auth_del/<int:id>", methods=['GET'])
@admin_login_req
@admin_auth
def auth_del(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()  # 查找错误404
    db.session.delete(auth)


    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='删除权限' + '<' + auth.name + '>',

    )
    db.session.add(oplog)
    db.session.commit()
    flash('删除成功', "ok")

    return redirect(url_for('admin.auth_list', page=1))


# 编辑权限
@admin.route("/auth_edit/<int:id>",methods=['GET','POST'])
@admin_login_req
@admin_auth
def auth_edit(id):
    form=AuthForm()
    auth = Auth.query.get_or_404(int(id))

    if request.method == 'GET':
        form.name.data = auth.name
        form.url.data = auth.url


    if form.validate_on_submit():
        data=form.data
        auth_count=Auth.query.filter_by(name=data['name']).count()
        if auth_count==1 and auth.name!=data['name']:
            flash('权限已存在','err')
            return redirect(url_for('admin.auth_edit',id=id))
        auth.name=data['name']
        auth.url=data['url']
        db.session.add(auth)


        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='编辑权限' + '<' + auth.name + '>',

        )
        db.session.add(oplog)

        db.session.commit()
        flash('更改成功','ok')
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/auth_edit.html",context=context,form=form)



# 角色列表
@admin.route("/role_list/<int:page>")
@admin_login_req
@admin_auth
def role_list(page):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/role_list.html",context=context,page=page_data)


# 角色添加
@admin.route("/role_add/",methods=['POST','GET'])
@admin_login_req
@admin_auth
def role_add():
    username = get_username()
    form=RoleForm()
    if form.validate_on_submit():
        data=form.data
        role_count=Role.query.filter_by(name=data['name']).count()
        if role_count==1:
            flash('已有该角色','err')
            return redirect(url_for('admin.role_add'))
        name=data['name']
        '''data['auths']:返回是一个数组,把他用逗号分隔成字符串'''
        auths=','.join(map(lambda v:str(v),data['auths']))
        role=Role(
            name=name,
            auths=auths,

        )
        db.session.add(role)
        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='添加角色' + '<' + role.name + '>',

        )
        db.session.add(oplog)
        db.session.commit()
        flash('角色添加成功','ok')
    context = {
        'username': username
    }
    return render_template("admin/role_add.html",context=context,form=form)

#删除角色
@admin.route("/role_del/<int:id>", methods=['GET'])
@admin_login_req
@admin_auth
def role_del(id=None):
    role = Role.query.filter_by(id=id).first_or_404()  # 查找错误404
    db.session.delete(role)

    oplog = Oplog(
        ip=request.remote_addr,
        admin_id=session["admin_id"],
        reson='删除角色' + '<' + role.name + '>',

    )
    db.session.add(oplog)
    db.session.commit()
    flash('删除成功', "ok")

    return redirect(url_for('admin.role_list', page=1))

#编辑角色
@admin.route("/role_edit/<int:id>",methods=['GET','POST'])
@admin_login_req
@admin_auth
def role_edit(id):
    username = get_username()
    form=RoleForm()
    role=Role.query.filter_by(id=id).first()
    if request.method=='GET':
        form.name.data=role.name
        auths=role.auths
        form.auths.data=list(map(lambda v:int(v),auths.split(',')))
    if form.validate_on_submit():
        data=form.data
        role_count=Role.query.filter_by(name=data['name']).count()
        if role_count==1 and data['name']!=role.name:
            flash('已有该角色','err')
            return redirect(url_for('admin.role_add'))
        name=data['name']
        '''data['auths']:返回是一个数组,把他用逗号分隔成字符串'''
        auths=','.join(map(lambda v:str(v),data['auths']))
        role.name=name
        role.auths=auths

        db.session.add(role)
        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='编辑角色' + '<' + role.name + '>',

        )
        db.session.add(oplog)
        db.session.commit()
        flash('编辑角色成功','ok')
    context = {
        'username': username
    }
    return render_template("admin/role_edit.html",context=context,form=form)


# 管理员添加
@admin.route("/admin_add/",methods=['GET','POST'])
@admin_auth
@admin_login_req
def admin_add():
    username = get_username()
    form=RegistAdminForm()
    if form.validate_on_submit():
        data=form.data
        admin_count=Admin.query.filter_by(name=data['name']).count()
        if admin_count!=0:
            flash('管理员姓名重复','err')
            return redirect(url_for('admin.admin_add'))
        admin = Admin(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            # is_super=1为普通管理员,=0为超级
            is_super=1,
            role_id=int(data['role_id']),
        )
        db.session.add(admin)

        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='添加管理员' + '<' + admin.name + '>',

        )
        db.session.add(oplog)
        db.session.commit()


    context = {
        'username': username
    }
    return render_template("admin/admin_add.html",context=context,form=form)

# 管理员列表
@admin.route("/admin_list/<int:page>")
@admin_login_req
@admin_auth
def admin_list(page=1):
    if page==None:
        page=1

    page_data = Admin.query.order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=10)  # per_page:一页显示数目
    username = get_username()
    context = {
        'username': username
    }
    return render_template("admin/admin_list.html",context=context,page=page_data)


#修改密码
@admin.route("/pwd/",methods=['POST',"GET"])
@admin_login_req
def pwd():
    username = get_username()
    form=Pwdform()
    admin=Admin.query.get_or_404(int(session['admin_id']))
    if form.validate_on_submit():
        data=form.data
        if not admin.check_pwd(data['pwd']):
            flash('旧密码错误','err')
            return redirect(url_for("admin.pwd"))
        print('dd')
        admin.pwd=generate_password_hash(data['newpwd'])
        db.session.add(admin)
        oplog = Oplog(
            ip=request.remote_addr,
            admin_id=session["admin_id"],
            reson='修改密码' + '<' + admin.name + '>',

        )
        db.session.add(oplog)
        db.session.commit()
        flash('修改成功','ok')
        return redirect(url_for('admin.pwd'))

    context = {
        'username': username
    }
    return render_template('admin/pwd.html',context=context,form=form)


# 获取用户名
def get_username():
    username = session.get('admin')
    if username is None:
        return None
    else:
        return username

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField,TextAreaField,SelectField,SelectMultipleField
from wtforms.validators import DataRequired, ValidationError,EqualTo
from app.models import Tag,Auth,Role
tag = Tag.query.all()
auth_list = Auth.query.all()
roles=Role.query.all()

class LoginForm(FlaskForm):
    """管理员登陆表单"""
    account = StringField(
        label='账号',
        validators=[
            DataRequired('请输入账号！')
        ],
        description='账号',
        render_kw={

            "class": "form-control",
            "placeholder": "请输入账号！",
            # 必填
            "required": "required",
            'id': 'account'
        }

    )

    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码！')
        ],
        description='密码',
        render_kw={

            "class": "form-control",
            "placeholder": "请输入密码！",
            # 必填
            "required": "required",
        }

    )
    submit = SubmitField(
        label='登陆',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }

    )


class TagForm(FlaskForm):
    """添加标签"""
    name = StringField(
        label='名称',
        validators=[
            DataRequired('请输入标签！')
        ],
        description='标签',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签！",
            # 必填
            "required": "required",

        },
    )
    submit = SubmitField(
        label='编辑',
        render_kw={

            "class": "btn btn-primary"
        }

    )

class MovieForm(FlaskForm):
    title = StringField(
        label='片名',
        validators=[
            DataRequired('请输入片名！')
        ],
        description='片名',
        render_kw={
            'class':"form-control" ,
            'id':"input_title" ,
            'placeholder':"请输入片名！",
            # 必填
            "required": "required",

        },
    )

    url=FileField(
        label='文件',
        validators=[
            DataRequired('请上传文件！')
        ],
        description='文件',


    )

    info=TextAreaField(
        label='介绍',
        validators=[
            DataRequired('请输入介绍！')
        ],
        description='介绍',
        render_kw={
            'class': "form-control",
            'rows':"10",
            "id":"input_info",
            # 必填
            "required": "required",

        },
    )

    logo=FileField(

        label="封面",
        validators=[
            DataRequired('请上传封面！')
        ],
        description="封面",
    )

    star=SelectField(
        label="星级",
        validators=[
            DataRequired('请选择星级！')
        ],
        description="星级",
        coerce=int,
        choices=[(1,"1星"),(2,"2星"),(3,"3星"),(4,"4星"),(5,"5星")],
        render_kw={
            "class":"form_control",
        }

    )

    tag_id = SelectField(

        label="标签",
        validators=[
            DataRequired('请选择标签！')
        ],
        description="标签",
        coerce=int,
        choices=[(v.id,v.name)for v in tag],
        render_kw={
            "class": "form_control",
        }
    )


    area = StringField(
        label='地区',
        validators=[
            DataRequired('请输入地区！')
        ],
        description='地区',
        render_kw={
            'class': "form-control",
            'id': "input_area",
            'placeholder': "请输入地区！",
            # 必填
            "required": "required",

        },
    )

    length= StringField(
        label='片长',
        validators=[
            DataRequired('请输入片长！')
        ],
        description='片长',
        render_kw={
            'class': "form-control",
            'id': "input_length",
            'placeholder': "请输入片长！",
            # 必填
            "required": "required",

        },
    )

    release_time = StringField(
        label='上映时间',
        validators=[
            DataRequired('请选择上映时间！')
        ],
        description='上映时间',
        render_kw={
            'class': "form-control",
            'id': "input_release_time",
            'placeholder': "请选择上映时间！",
            # 必填
            "required": "required",

        },
    )

    submit = SubmitField(
        label='编辑',
        render_kw={

            "class": "btn btn-primary"
        }

    )



class PreviewForm(FlaskForm):
    """添加标题"""
    title = StringField(
        label='预告标题',
        validators=[
            DataRequired('请输入预告标题！')
        ],
        description='预告标题',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告标题！",
            # 必填
            "required": "required",

        },
    )

    logo=FileField(
        label='预告封面',
        validators=[
            DataRequired('请上传封面！')
        ],
        description='封面',


    )
    submit = SubmitField(
        label='编辑',
        render_kw={

            "class": "btn btn-primary"
        }

    )





class RegistAdminForm(FlaskForm):
    name=StringField(
        label='管理员名称',
        validators=[
            DataRequired('请输入管理员！')
        ],
        description='名称',
        render_kw={

            "class": "form-control",
            "placeholder": "名称",
            # 必填
            "required": "required",

        }
    )


    pwd=PasswordField(
        label='管理员密码',
        validators=[
            DataRequired('请输入密码'),
        ],
        description='密码',
        render_kw={
            'class': 'form-control ',
            "placeholder": "请输入管理员密码！",
        }
    )

    repwd = PasswordField(
        label='管理员重复密码',
        validators=[
            DataRequired('请再输入一次密码'),
            EqualTo('pwd','两次密码不一致'),


        ],
        description='确认密码',
        render_kw={
            'class': 'form-control ',
            "placeholder": "确认密码",
        }
    )

    role_id = SelectField(

        label="所属角色",
        validators=[
            DataRequired('请选择角色！')
        ],
        description="角色",
        coerce=int,
        choices=[(v.id, v.name) for v in roles],
        render_kw={
            "class": "form_control",
        }
    )
    submit=SubmitField(
        label='添加',
        render_kw={
            'class':'btn btn-primary',
        }
    )


class AuthForm(FlaskForm):
    name = StringField(
        label='权限名称',
        validators=[
            DataRequired('请输入权限名称！')
        ],
        description='权限名称',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称！",
            # 必填
            "required": "required",

        },
    )
    url = StringField(
        label='权限地址',
        validators=[
            DataRequired('请输入权限地址！')
        ],
        description='权限地址',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址！",
            # 必填
            "required": "required",

        },

    )
    submit = SubmitField(
        label='编辑',
        render_kw={

            "class": "btn btn-primary"
        }

    )


class RoleForm(FlaskForm):
    name = StringField(
        label='角色名称',
        validators=[
            DataRequired('请输入角色名称！')
        ],
        description='角色名称',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称！",
            # 必填
            "required": "required",

        },
    )

    # 多选框
    auths = SelectMultipleField(
        label='操作权限',
        validators=[
            DataRequired('请选择操作权限！')
        ],

        coerce=int,
        choices=[(v.id, v.name) for v in auth_list],
        description='操作权限',
        render_kw={
            "class": "form-control",

        },

    )
    submit = SubmitField(
        label='编辑',
        render_kw={
            "class": "btn btn-primary"
        }

    )


class Pwdform(FlaskForm):
    pwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired('请输入旧密码'),
        ],
        description='旧密码',
        render_kw={
            'class': 'form-control ',
            "placeholder": "请输入旧密码！",
        }
    )

    newpwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired('请输入新密码'),
        ],
        description='新密码',
        render_kw={
            'class': 'form-control ',
            "placeholder": "请输入新密码！",
        }
    )

    repwd = PasswordField(
        label='重复新密码',
        validators=[
            DataRequired('请再输入新密码'),
            EqualTo('newpwd', '两次密码不一致'),

        ],
        description='确认密码',
        render_kw={
            'class': 'form-control ',
            "placeholder": "确认密码",
        }
    )
    submit = SubmitField(
        label='修改',
        render_kw={
            "class": "glyphicon glyphicon-edit"
        }

    )





from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField,TextAreaField,SelectField
from wtforms.validators import DataRequired, ValidationError,Email,Regexp,EqualTo

class RegistForm(FlaskForm):
    name=StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称！')
        ],
        description='昵称',
        render_kw={

            "class": "form-control input-lg",
            "placeholder": "昵称",

            # 必填
            "required": "required",

        }
    )



    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入昵称！'),
            Email('邮箱格式不正确')
        ],
        description='昵称',
        render_kw={

            "class": "form-control input-lg",
            "placeholder": "邮箱",
            # 必填
            "required": "required",

        }
    )

    phone=StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机号'),
            Regexp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$",message='手机格式不正确'),
        ],
        description='手机',
        render_kw={
            'class':'form-control input-lg',
            "placeholder": "手机",
        }
    )

    pwd=PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码'),
        ],
        description='密码',
        render_kw={
            'class': 'form-control input-lg',
            "placeholder": "密码",
        }
    )

    repwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('请再输入一次密码'),
            EqualTo('pwd','两次密码不一致'),


        ],
        description='确认密码',
        render_kw={
            'class': 'form-control input-lg',
            "placeholder": "确认密码",
        }
    )
    submit=SubmitField(
        label='注册',
        render_kw={
            'class':'btn btn-lg btn-success btn-block',
        }
    )

class LoginForm(FlaskForm):
    name=StringField(
        label='账号',
        validators=[
            DataRequired('请输入账号！')
        ],
        description='用户名/邮箱/手机号码',
        render_kw={

            "class": "form-control input-lg",
            "placeholder": "用户名/邮箱/手机号码",

            # 必填
            "required": "required",

        }
    )
    pwd=PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码'),

        ],
        description='密码',
        render_kw={
            'class': 'form-control input-lg',
            "placeholder": "密码",
        }
    )

    submit = SubmitField(
        label='登录',
        render_kw={
            'class': 'btn btn-lg btn-success btn-block',
        }
    )

class UserForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称！')
        ],
        description='昵称',
        render_kw={

            "class": "form-control",
            "placeholder": "昵称",

            # 必填
            "required": "required",

        }
    )

    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入昵称！'),
            Email('邮箱格式不正确')
        ],
        description='昵称',
        render_kw={

            "class": "form-control",
            "placeholder": "邮箱",
            # 必填
            "required": "required",

        }
    )

    face = FileField(
        label="头像",
        validators=[

        ],
        description="头像",
    )

    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机号'),
            Regexp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$", message='手机格式不正确'),
        ],
        description='手机',
        render_kw={
            'class': 'form-control',
            "placeholder": "手机",
        }
    )

    info = TextAreaField(
        label='简介',
        validators=[

        ],
        description='简介',
        render_kw={
            'class': "form-control",
            'rows': "10",



        },
    )

    submit = SubmitField(
        label='提交',
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
            "class": "btn btn-primary"
        }

    )

class CommentForm(FlaskForm):

    content = TextAreaField(
        label='评论',
        validators=[
             DataRequired('请输入评论'),
        ],
        description='评论',
        render_kw={
            'rows': "10",
            'id':'input_content',
        },
    )


    submit = SubmitField(
        label='提交评论',
        render_kw={
            "class": "btn btn-success",
            "id" : "btn-sub"
        }

    )



import os
from flask_admin import Admin
from models import db, User, Marvel, Dc, Other, Favoritos
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Hero DB Admin', template_mode='bootstrap3')
    
    class FavoritosAdmin(ModelView):

        column_list = ("id", "user_id", "id_marvel", "id_dc", "id_other")
        form_columns = ("user_id", "id_marvel", "id_dc", "id_other")

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Marvel, db.session))
    admin.add_view(ModelView(Dc, db.session))
    admin.add_view(ModelView(Other, db.session))

    admin.add_view(FavoritosAdmin(Favoritos, db.session))
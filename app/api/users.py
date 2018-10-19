# from flask import jsonify, request, url_for
# from app import db
# from app.models import User
# from app.api import bp
#
#
#
# @bp.route('/user/<int:id>', methods=['GET'])
# @token_auth.login_required
# def get_user(id):
#     return jsonify(User.query.get_or_404(id).to_dict())
#
#
# @bp.route('/user', methods=['GET'])
# @token_auth.login_required
# def get_users():
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 10, type=int), 100)
#     data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
#     return jsonify(data)
#
#
# @bp.route('/user/<int:id>/followers', methods=['GET'])
# @token_auth.login_required
# def get_followers(id):
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 10, type=int), 100)
#     data = User.to_collection_dict(user.followers, page, per_page,
#                                    'api.get_followers', id=id)
#     return jsonify(data)
#
#
# @bp.route('/user/<int:id>/followed', methods=['GET'])
# @token_auth.login_required
# def get_followed(id):
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 10, type=int), 100)
#     data = User.to_collection_dict(user.followed, page, per_page,
#                                    'api.get_followed', id=id)
#     return jsonify(data)
#
#
# @bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json() or {}
#     if 'username' not in data or 'email' not in data or 'password' not in data:
#         return bad_request('must include username, email and password fields')
#     if User.query.filter_by(username=data['username']).first():
#         return bad_request('please use a different username')
#     if User.query.filter_by(email=data['email']).first():
#         return bad_request('please use a different email address')
#     user = User()
#     user.from_dict(data)
#     db.session.add(user)
#     db.session.commit()
#     response = jsonify(user.to_dict())
#     response.status_code = 201
#     return response
#
#
# @bp.route('/login', methods=['POST'])
# @token_auth.login_required
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         return redirect(url_for('index'))
#     return render_template('login.html', title='Sign In', form=form)
#
#
#     data = request.get_json() or {}
#     if 'username' not in data or 'password' not in data:
#         return bad_request('must include username and password')
#
#     user = User.query.filter_by(username=data['username']).first()
#     if not :
#         return bad_request('用户名')
#
#     if 'username' in data and User.query.filter_by(username=data['username']).first():
#         return bad_request('please use a different username')
#
#     user.from_dict(data, new_user=False)
#     db.session.commit()
#     return jsonify(user.to_dict())

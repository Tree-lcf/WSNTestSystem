from app import create_app, db
from app.models import User, Project

app = create_app()
# map_list = app.url_map
# print(map_list)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Project': Project}


# if __name__ == '__main__':
#     app.run(debug=True, host='10.16.6.84', port=5000)

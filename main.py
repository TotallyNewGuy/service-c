import os
from quart import Quart
from quart_cors import cors
from dotenv import load_dotenv

from db_util import init_db
from redis_util import init_redis
from query_blueprint import query_blueprint


def create_app():
    load_dotenv()
    
    app = Quart(__name__)
    # enable CORS
    app = cors(app, allow_origin="*")
    app.register_blueprint(query_blueprint)
    return app


app = create_app()


@app.before_serving
async def start_background_task():
    init_db()
    await init_redis()


@app.route("/")
async def hello_world():
    return "<p>Hello World from Service C!</p>"


if __name__ == "__main__":
    # Run the Quart(Flask) app when run this Python file
    DEBUG = os.getenv("DEBUG").lower() == 'true'
    port = int(os.getenv("PORT", 8080))
    print(f"listening post: {port}")
    app.run(debug=DEBUG, port=port, host="0.0.0.0")
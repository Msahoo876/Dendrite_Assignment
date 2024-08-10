from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_graphql import GraphQLView
from flask_cors import CORS
import graphene
import stripe
import os
import secrets
from keycloak import KeycloakOpenID

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Ensure the upload folder exists
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

# Keycloak setup
KEYCLOAK_SERVER_URL = "http://localhost:8089/auth/"
KEYCLOAK_REALM_NAME = "dendrite"
KEYCLOAK_CLIENT_ID = "public-client"
KEYCLOAK_CLIENT_SECRET = "NEHyC8IwCOcREcnGxZ9uI99lTxMkCOiz"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 realm_name=KEYCLOAK_REALM_NAME,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET)

def get_user_info(token):
    return keycloak_openid.userinfo(token)

def verify_token(token):
    options = {"verify_signature": True, "verify_aud": True, "exp": True}
    return keycloak_openid.decode_token(token, key=keycloak_openid.public_key(), options=options)

# Stripe setup
stripe.api_key = "sk_test_51PleF2JGCm1g3pVzzpyqRdt7yW486fV9EWpaJU1iNQJj2tdTHhejX3QQ80ehkLG0o3SgvqEeZ7qAG3Yrq1JHVeg500O7pm7cv2"


def create_payment_intent(amount):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        payment_method_types=["card"]
    )

# Dummy data store for To-Dos
todos = []

class Todo(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    time = graphene.String()
    image = graphene.String()

class Query(graphene.ObjectType):
    todos = graphene.List(Todo)

    def resolve_todos(self, info):
        return todos

class AddTodo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        time = graphene.String(required=True)
        image = graphene.String(required=False)  # Optional image for Pro users

    todo = graphene.Field(Todo)

    def mutate(self, info, title, description, time, image=None):
        if image:
            image_path = f"static/uploads/{image}"
            # Save the uploaded image to the static/uploads directory
            with open(image_path, "wb") as f:
                f.write(image.encode())  # Assuming image is in base64 or similar format
        else:
            image_path = None

        todo = {
            "id": len(todos) + 1,
            "title": title,
            "description": description,
            "time": time,
            "image": image_path,
        }
        todos.append(todo)
        return AddTodo(todo=todo)

class DeleteTodo(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        global todos
        todos = [todo for todo in todos if todo['id'] != id]
        return DeleteTodo(ok=True)

class Mutation(graphene.ObjectType):
    add_todo = AddTodo.Field()
    delete_todo = DeleteTodo.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

# Basic UI Route
@app.route('/')
def index():
    return render_template('index.html')

# Stripe payment endpoint
@app.route('/buy_pro', methods=['GET'])
def buy_pro():
    amount = 500  # $5.00 in cents
    payment_intent = create_payment_intent(amount)
    return render_template('index.html', client_secret=payment_intent['client_secret'])

# Middleware to check authentication for GraphQL requests
@app.before_request
def check_auth():
    if request.path.startswith('/graphql'):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return {'message': 'Missing authorization token'}, 401

        token = auth_header.split(" ")[1]
        try:
            verify_token(token)
        except Exception as e:
            return {'message': 'Invalid token', 'error': str(e)}, 401

if __name__ == '__main__':
    app.run(debug=True)

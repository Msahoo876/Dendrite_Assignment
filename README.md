# To-Do List Application

A simple To-Do List web application that uses Flask and GraphQL, with Keycloak for authentication and Stripe for payment. Users can manage their to-do items and purchase a Pro license to upload images.

## Features

- **Authentication**: Secure login with Keycloak.
- **CRUD Operations**: List, add, delete, and edit to-do items.
- **Pro License**: Option to buy a Pro license to upload images with to-do items.
- **GraphQL API**: All operations are handled through a GraphQL API.
- **Payment Integration**: Stripe integration for Pro license purchases.

## Technologies Used

- **Backend**: Flask, GraphQL
- **Authentication**: Keycloak
- **Payment**: Stripe
- **Frontend**: HTML, CSS
- **Database**: In-memory store (list)

## Setup

### Prerequisites

- Python 3.x
- Docker (for Keycloak)
- Docker Compose (for Keycloak)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Msahoo876/Dendrite_Assignment.git
   cd Dendrite_Assignment
   
2. **Create Virtual Environment(optional)**;
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   
4. **Activate Virtual Environment**;
   dendrite\Scripts\activate
   
6. **Install Dependencies(optional)**;
   pip install -r requirements.txt

7. **Run the Application**;
   python app.py
   
### Output Screen

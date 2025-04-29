import streamlit as st
import requests
import os
from datetime import datetime

# Backend URL configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
print(f"Using BACKEND_URL: {BACKEND_URL}")  # Add this line
st.write(f"Using BACKEND_URL: {BACKEND_URL}")  # Optional: also display in Streamlit UI

# Function to register a new user
def register(username, email, first_name, last_name, password):
    url = f"{BACKEND_URL}/auth/"
    data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return True, "Registration successful. Please log in."
        else:
            return False, response.json().get("detail", "Registration failed.")
    except requests.RequestException as e:
        return False, str(e)

# Function to log in and retrieve an access token
def login(username, password):
    url = f"{BACKEND_URL}/auth/token"
    data = {"username": username, "password": password}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return True, token
        else:
            return False, response.json().get("detail", "Login failed.")
    except requests.RequestException as e:
        return False, str(e)

# Helper function for authenticated API requests
def make_auth_request(method, endpoint, data=None):
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return False, "Invalid method"
        
        if response.status_code in [200, 201, 204]:
            return True, response.json() if response.status_code != 204 else None
        else:
            error_detail = response.json().get("detail", "Operation failed.")
            return False, f"Error {response.status_code}: {error_detail}"
    except requests.RequestException as e:
        return False, f"Request failed: {str(e)}"

# Todo operation functions
def get_todos():
    return make_auth_request("GET", "/todos/")

def add_todo(description, due_date, priority):
    data = {
        "description": description,
        "due_date": due_date.isoformat(),
        "priority": priority
    }
    return make_auth_request("POST", "/todos/", data)

def update_todo(todo_id, description, due_date, priority):
    data = {
        "description": description,
        "due_date": due_date.isoformat(),
        "priority": priority
    }
    return make_auth_request("PUT", f"/todos/{todo_id}", data)

def complete_todo(todo_id):
    return make_auth_request("PUT", f"/todos/{todo_id}/complete")

def delete_todo(todo_id):
    return make_auth_request("DELETE", f"/todos/{todo_id}")

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

# Main application function
def main():
    st.sidebar.title("Authentication")
    if st.session_state.token is None:
        choice = st.sidebar.selectbox("Select", ["Login", "Register"])
        if choice == "Register":
            st.sidebar.subheader("Register")
            reg_username = st.sidebar.text_input("Username", key="reg_username")
            reg_email = st.sidebar.text_input("Email", key="reg_email")
            reg_first_name = st.sidebar.text_input("First Name", key="reg_first_name")
            reg_last_name = st.sidebar.text_input("Last Name", key="reg_last_name")
            reg_password = st.sidebar.text_input("Password", type="password", key="reg_password")
            if st.sidebar.button("Register"):
                success, message = register(reg_username, reg_email, reg_first_name, reg_last_name, reg_password)
                if success:
                    st.sidebar.success(message)
                else:
                    st.sidebar.error(message)
        else:
            st.sidebar.subheader("Login")
            login_username = st.sidebar.text_input("Username", key="login_username")
            login_password = st.sidebar.text_input("Password", type="password", key="login_password")
            if st.sidebar.button("Login"):
                success, result = login(login_username, login_password)
                if success:
                    st.session_state.token = result
                    st.session_state.username = login_username
                    st.sidebar.success("Logged in successfully.")
                    st.rerun()
                else:
                    st.sidebar.error(result)
    else:
        st.sidebar.write(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.sidebar.success("Logged out successfully.")
            st.rerun()

    # Todo management interface
    if st.session_state.token is None:
        st.write("Please log in to manage your todos.")
    else:
        st.title("Todo List")
        success, data = get_todos()
        if success:
            if data:
                for todo in data:
                    todo_details = (
                        f"ID: {todo.get('id', 'N/A')}, "
                        f"Description: {todo.get('description', 'N/A')}, "
                        f"Due Date: {todo.get('due_date', 'N/A')}, "
                        f"Priority: {todo.get('priority', 'N/A')}, "
                        f"Completed: {todo.get('is_completed', False)}, "
                        f"Completed At: {todo.get('completed_at', 'N/A')}"
                    )
                    st.write(todo_details)
            else:
                st.write("No todos found.")
        else:
            st.error(data)

        st.subheader("Add New Todo")
        new_description = st.text_input("Description", key="add_description")
        new_due_date = st.date_input("Due Date", key="add_due_date")
        new_priority = st.number_input("Priority", min_value=1, max_value=5, value=1, key="add_priority")
        if st.button("Add Todo"):
            if new_description:
                success, result = add_todo(new_description, new_due_date, new_priority)
                if success:
                    st.success("Todo added successfully.")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please provide a description.")

        st.subheader("Update Todo")
        update_id = st.text_input("Todo ID to update", key="update_id")
        update_description = st.text_input("New Description", key="update_description")
        update_due_date = st.date_input("New Due Date", key="update_due_date")
        update_priority = st.number_input("New Priority", min_value=1, max_value=5, value=1, key="update_priority")
        if st.button("Update Todo"):
            if update_id and update_description:
                success, result = update_todo(update_id, update_description, update_due_date, update_priority)
                if success:
                    st.success("Todo updated successfully.")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please provide Todo ID and new description.")

        st.subheader("Complete Todo")
        complete_id = st.text_input("Todo ID to complete", key="complete_id")
        if st.button("Complete Todo"):
            if complete_id:
                success, result = complete_todo(complete_id)
                if success:
                    st.success("Todo marked as complete.")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please provide a Todo ID.")

        st.subheader("Delete Todo")
        delete_id = st.text_input("Todo ID to delete", key="delete_id")
        if st.button("Delete Todo"):
            if delete_id:
                success, result = delete_todo(delete_id)
                if success:
                    st.success("Todo deleted successfully.")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please provide a Todo ID.")

if __name__ == "__main__":
    main()
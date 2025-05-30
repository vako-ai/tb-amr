import streamlit as st
import pandas as pd
import datetime
import hashlib
import auth
import utils
from db_manager import get_connection

def show():
    """Display the user management page"""
    # Only allow admins to access this page
    if st.session_state.user_role != "admin":
        st.error("You don't have permission to access this page.")
        return
    
    st.title("User Management")
    
    # Connect to the PostgreSQL database
    conn = get_connection()
    
    # Create tabs for different user management features
    tab1, tab2, tab3 = st.tabs([
        "User List", 
        "Add User", 
        "User Activity"
    ])
    
    with tab1:
        show_user_list(conn)
    
    with tab2:
        show_add_user(conn)
    
    with tab3:
        show_user_activity(conn)
    
    # Close database connection
    conn.close()

def show_user_list(conn):
    """Display list of users"""
    st.header("User List")
    
    try:
        # Get all users from the database
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, role, created_at, last_login
            FROM users
            ORDER BY username
            """
        )
        users = cursor.fetchall()
        
        if not users:
            st.info("No users found in the system.")
            return
        
        # Create DataFrame for display
        user_df = pd.DataFrame(
            users,
            columns=['ID', 'Username', 'Role', 'Created At', 'Last Login']
        )
        
        # Format datetime columns
        for date_col in ['Created At', 'Last Login']:
            user_df[date_col] = user_df[date_col].apply(
                lambda x: utils.format_datetime(x) if x else "Never"
            )
        
        # Display user table
        st.dataframe(
            user_df[['Username', 'Role', 'Created At', 'Last Login']],
            use_container_width=True,
            hide_index=True
        )
        
        # User actions
        st.subheader("User Actions")
        
        # Select user
        selected_user = st.selectbox(
            "Select User",
            options=user_df['Username'].tolist(),
            key="selected_user_for_action"
        )
        
        if selected_user:
            # Get user ID and current role
            user_id = user_df[user_df['Username'] == selected_user]['ID'].iloc[0]
            current_role = user_df[user_df['Username'] == selected_user]['Role'].iloc[0]
            
            # Action selection
            action = st.radio(
                "Select Action",
                ["Change Role", "Reset Password", "Delete User"],
                key="user_action"
            )
            
            if action == "Change Role":
                # Role change
                new_role = st.selectbox(
                    "New Role",
                    options=["user", "admin"],
                    index=0 if current_role == "user" else 1
                )
                
                if st.button("Change Role"):
                    if selected_user == st.session_state.username and new_role != "admin":
                        st.error("You cannot remove your own admin privileges.")
                    else:
                        try:
                            cursor.execute(
                                "UPDATE users SET role = %s WHERE id = %s",
                                (new_role, user_id)
                            )
                            conn.commit()
                            st.success(f"Changed {selected_user}'s role to {new_role}")
                            
                            # Log the activity
                            admin_id = utils.get_user_id(st.session_state.username, conn)
                            utils.log_activity(
                                conn, 
                                admin_id, 
                                "Changed User Role", 
                                {"username": selected_user, "new_role": new_role}
                            )
                            
                            # Refresh page
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error changing role: {e}")
            
            elif action == "Reset Password":
                # Password reset
                new_password = st.text_input(
                    "New Password",
                    type="password",
                    key="new_password_reset"
                )
                
                confirm_password = st.text_input(
                    "Confirm New Password",
                    type="password",
                    key="confirm_password_reset"
                )
                
                if st.button("Reset Password"):
                    if not new_password:
                        st.error("Password cannot be empty")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        try:
                            # Hash the new password
                            password_hash = auth.hash_password(new_password)
                            
                            cursor.execute(
                                "UPDATE users SET password_hash = %s WHERE id = %s",
                                (password_hash, user_id)
                            )
                            conn.commit()
                            st.success(f"Reset password for {selected_user}")
                            
                            # Log the activity
                            admin_id = utils.get_user_id(st.session_state.username, conn)
                            utils.log_activity(
                                conn, 
                                admin_id, 
                                "Reset User Password", 
                                {"username": selected_user}
                            )
                        except Exception as e:
                            st.error(f"Error resetting password: {e}")
            
            elif action == "Delete User":
                # User deletion with confirmation
                st.warning(f"Are you sure you want to delete user {selected_user}? This action cannot be undone.")
                
                confirm_delete = st.text_input(
                    f"Type '{selected_user}' to confirm deletion",
                    key="confirm_delete_user"
                )
                
                if st.button("Delete User"):
                    if confirm_delete != selected_user:
                        st.error("Username confirmation does not match")
                    elif selected_user == st.session_state.username:
                        st.error("You cannot delete your own account")
                    else:
                        try:
                            cursor.execute(
                                "DELETE FROM users WHERE id = ?",
                                (user_id,)
                            )
                            conn.commit()
                            st.success(f"Deleted user {selected_user}")
                            
                            # Log the activity
                            admin_id = utils.get_user_id(st.session_state.username, conn)
                            utils.log_activity(
                                conn, 
                                admin_id, 
                                "Deleted User", 
                                {"username": selected_user}
                            )
                            
                            # Refresh page
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting user: {e}")
    
    except Exception as e:
        st.error(f"Error retrieving user list: {e}")

def show_add_user(conn):
    """Display add user form"""
    st.header("Add New User")
    
    with st.form("add_user_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        role = st.selectbox(
            "Role",
            options=["user", "admin"],
            index=0
        )
        
        submitted = st.form_submit_button("Create User")
        
        if submitted:
            if not username or not password:
                st.error("Username and password are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Create new user
                success, message = auth.create_user(username, password, role)
                
                if success:
                    st.success(f"User '{username}' created successfully")
                    
                    # Log the activity
                    admin_id = utils.get_user_id(st.session_state.username, conn)
                    utils.log_activity(
                        conn, 
                        admin_id, 
                        "Created New User", 
                        {"username": username, "role": role}
                    )
                else:
                    st.error(f"Failed to create user: {message}")

def show_user_activity(conn):
    """Display user activity logs"""
    st.header("User Activity Log")
    
    # Date range filter
    st.subheader("Filter Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get earliest log date
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(timestamp) FROM activity_log")
            min_date = cursor.fetchone()[0]
            
            if min_date:
                min_date = datetime.datetime.fromisoformat(min_date).date()
            else:
                min_date = datetime.date.today() - datetime.timedelta(days=30)
        except:
            min_date = datetime.date.today() - datetime.timedelta(days=30)
        
        start_date = st.date_input(
            "Start Date",
            value=min_date
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.date.today()
        )
    
    # User filter
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT username FROM users ORDER BY username")
        usernames = [row[0] for row in cursor.fetchall()]
        
        selected_users = st.multiselect(
            "Filter by User",
            options=usernames,
            default=None
        )
    except:
        selected_users = []
    
    # Activity type filter
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT activity_type FROM activity_log ORDER BY activity_type")
        activity_types = [row[0] for row in cursor.fetchall()]
        
        selected_activities = st.multiselect(
            "Filter by Activity Type",
            options=activity_types,
            default=None
        )
    except:
        selected_activities = []
    
    # Build query
    query = """
    SELECT al.id, u.username, al.activity_type, al.details, al.timestamp
    FROM activity_log al
    JOIN users u ON al.user_id = u.id
    WHERE al.timestamp BETWEEN ? AND ?
    """
    
    params = [
        start_date.isoformat(), 
        (end_date + datetime.timedelta(days=1)).isoformat()
    ]
    
    if selected_users:
        placeholders = ", ".join(["?"] * len(selected_users))
        query += f" AND u.username IN ({placeholders})"
        params.extend(selected_users)
    
    if selected_activities:
        placeholders = ", ".join(["?"] * len(selected_activities))
        query += f" AND al.activity_type IN ({placeholders})"
        params.extend(selected_activities)
    
    query += " ORDER BY al.timestamp DESC"
    
    # Execute query
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        activities = cursor.fetchall()
        
        if not activities:
            st.info("No activity logs found for the selected filters")
            return
        
        # Create DataFrame for display
        activity_df = pd.DataFrame(
            activities,
            columns=['ID', 'Username', 'Activity Type', 'Details', 'Timestamp']
        )
        
        # Format datetime and details
        activity_df['Timestamp'] = activity_df['Timestamp'].apply(utils.format_datetime)
        
        # Parse details JSON
        def format_details(details_json):
            if not details_json:
                return ""
            try:
                details = json.loads(details_json)
                return ", ".join([f"{k}: {v}" for k, v in details.items()])
            except:
                return details_json
        
        activity_df['Details'] = activity_df['Details'].apply(format_details)
        
        # Display activity table
        st.dataframe(
            activity_df[['Username', 'Activity Type', 'Details', 'Timestamp']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        if st.button("Export Activity Log"):
            csv = activity_df[['Username', 'Activity Type', 'Details', 'Timestamp']].to_csv(index=False)
            filename = f"activity_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error retrieving activity logs: {e}")
